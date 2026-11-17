import pandas as pd
import pyomo.environ as pyo


def optimize_bess(profile, candidates, config):
    """
    Formulate and solve optimal BESS placement, sizing, and fleet dispatch
    for the Sri Lanka transmission grid.
    """
    profile = profile.copy().reset_index(drop=True)

    candidates = candidates[
        candidates["eligible"].astype(bool)
    ].copy().reset_index(drop=True)

    if profile.empty:
        raise ValueError("Hourly profile is empty.")

    if candidates.empty:
        raise ValueError("No eligible candidate sites.")

    required = ["demand_mw", "solar_mw"]
    if not set(required).issubset(profile.columns):
        raise ValueError("Profile must contain demand_mw and solar_mw.")

    if "site_cost_factor" not in candidates.columns:
        candidates["site_cost_factor"] = 1.0

    n = len(profile)
    sites = candidates["bus_id"].astype(str).tolist()

    battery = config["battery"]
    opt = config["optimization"]

    dt = opt.get("time_step_hours", 1)
    eta_rt = battery["round_trip_efficiency"]
    eta_charge = eta_rt ** 0.5
    eta_discharge = eta_rt ** 0.5

    duration = battery["duration_hours"]
    life = battery["lifetime_years"]
    discount = battery["discount_rate"]

    crf = (
        discount * (1 + discount) ** life
        / ((1 + discount) ** life - 1)
    )

    annualization_scale = (
        365 / opt.get("profile_days_represented", 365)
    )

    solar = profile["solar_mw"].astype(float).tolist()
    demand = profile["demand_mw"].astype(float).tolist()
    net_demand = [d - s for d, s in zip(demand, solar)]
    max_net_demand = max(net_demand)

    target_total_mw = float(
        opt.get("target_total_power_mw", opt.get("min_total_power_mw", 50.0))
    )

    m = pyo.ConcreteModel()

    m.I = pyo.Set(initialize=sites)
    m.T = pyo.RangeSet(0, n - 1)

    # Nodal installation and capacity variables
    m.build = pyo.Var(m.I, domain=pyo.Binary)
    m.power = pyo.Var(m.I, domain=pyo.NonNegativeReals)
    m.energy = pyo.Var(m.I, domain=pyo.NonNegativeReals)
    m.total_power = pyo.Var(domain=pyo.NonNegativeReals)
    m.total_energy = pyo.Var(domain=pyo.NonNegativeReals)

    # Fleet-wide dispatch variables across time
    m.charge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.discharge = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.soc = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.curtailment = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.residual = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.peak = pyo.Var(domain=pyo.NonNegativeReals)

    # Aggregated fleet capacity definitions
    m.sum_power = pyo.Constraint(
        expr=m.total_power == sum(m.power[i] for i in m.I)
    )
    m.sum_energy = pyo.Constraint(
        expr=m.total_energy == sum(m.energy[i] for i in m.I)
    )

    # Minimum target capacity and maximum fleet limits
    if target_total_mw > 0:
        m.min_total_power = pyo.Constraint(
            expr=m.total_power >= target_total_mw
        )

    m.max_total_power = pyo.Constraint(
        expr=m.total_power <= opt.get("maximum_total_power_mw", 300.0)
    )

    m.site_limit = pyo.Constraint(
        expr=sum(m.build[i] for i in m.I)
        <= battery.get("maximum_number_of_sites", 5)
    )

    # Siting constraints per substation
    for i in sites:
        m.add_component(
            f"max_power_{i}",
            pyo.Constraint(
                expr=m.power[i] <= battery["maximum_power_per_site_mw"] * m.build[i]
            )
        )
        m.add_component(
            f"min_power_{i}",
            pyo.Constraint(
                expr=m.power[i] >= battery["minimum_power_mw"] * m.build[i]
            )
        )
        m.add_component(
            f"duration_{i}",
            pyo.Constraint(
                expr=m.energy[i] == duration * m.power[i]
            )
        )

    # Fleet dispatch and dynamic constraints across 744 hours
    for t in range(n):
        m.add_component(f"c_lim_{t}", pyo.Constraint(expr=m.charge[t] <= m.total_power))
        m.add_component(f"d_lim_{t}", pyo.Constraint(expr=m.discharge[t] <= m.total_power))
        m.add_component(f"s_lim_{t}", pyo.Constraint(expr=m.soc[t] <= m.total_energy))

        prev = n - 1 if t == 0 else t - 1
        m.add_component(
            f"soc_bal_{t}",
            pyo.Constraint(
                expr=m.soc[t] == m.soc[prev]
                + eta_charge * m.charge[t] * dt
                - m.discharge[t] * dt / eta_discharge
            )
        )

        # Solar absorption: charging cannot exceed available solar output
        m.add_component(
            f"solar_charge_{t}",
            pyo.Constraint(expr=m.charge[t] <= solar[t])
        )

        # Unabsorbed surplus solar curtailment definition
        m.add_component(
            f"curt_def_{t}",
            pyo.Constraint(
                expr=m.curtailment[t] >= solar[t] - m.charge[t] - demand[t]
            )
        )

        # Residual thermal demand to be served
        m.add_component(
            f"residual_bal_{t}",
            pyo.Constraint(
                expr=m.residual[t] == (
                    demand[t] - solar[t]
                    + m.charge[t]
                    - m.discharge[t]
                    + m.curtailment[t]
                )
            )
        )

        # Peak tracking
        m.add_component(
            f"peak_lim_{t}",
            pyo.Constraint(expr=m.peak >= m.residual[t])
        )

    # Annualized objective function
    def objective_rule(m):
        investment = sum(
            candidates.loc[j, "site_cost_factor"]
            * (
                battery["power_cost_usd_per_kw"] * 1000 * m.power[i]
                + battery["energy_cost_usd_per_kwh"] * 1000 * m.energy[i]
            )
            for j, i in enumerate(sites)
        )

        annualized_investment = crf * investment

        annual_om = sum(
            battery["annual_om_usd_per_kw_year"] * 1000 * m.power[i]
            for i in m.I
        )

        curtailment_cost = (
            annualization_scale
            * opt["curtailment_penalty_usd_per_mwh"]
            * sum(m.curtailment[t] * dt for t in m.T)
        )

        peak_benefit = (
            -opt["peak_reduction_value_usd_per_mw_year"]
            * (max_net_demand - m.peak)
        )

        return (
            annualized_investment
            + annual_om
            + curtailment_cost
            + peak_benefit
        )

    m.objective = pyo.Objective(rule=objective_rule, sense=pyo.minimize)

    solver = pyo.SolverFactory("appsi_highs")
    if not solver.available(exception_flag=False):
        raise RuntimeError("HiGHS solver not found. Install highspy.")

    result = solver.solve(m, tee=False)
    condition = result.solver.termination_condition
    if condition != pyo.TerminationCondition.optimal:
        raise RuntimeError(f"Optimization not optimal: {condition}")

    # Extract selected battery locations
    selected = []
    for i in sites:
        p_val = pyo.value(m.power[i])
        if pyo.value(m.build[i]) > 0.5 and p_val > 0.01:
            site_factor = float(
                candidates.loc[
                    candidates["bus_id"].astype(str) == i,
                    "site_cost_factor"
                ].iloc[0]
            )
            selected.append({
                "bus_id": i,
                "power_mw": round(p_val, 2),
                "energy_mwh": round(pyo.value(m.energy[i]), 2),
                "site_cost_factor": site_factor
            })

    # Hourly dispatch time series
    dispatch_rows = []
    for t in range(n):
        charge_val = pyo.value(m.charge[t])
        discharge_val = pyo.value(m.discharge[t])
        residual_val = pyo.value(m.residual[t])
        curt_val = pyo.value(m.curtailment[t])
        surplus_val = max(0.0, solar[t] - demand[t])

        dispatch_rows.append({
            "timestamp": profile.loc[t, "timestamp"] if "timestamp" in profile.columns else t,
            "solar_mw": solar[t],
            "demand_mw": demand[t],
            "solar_surplus_mw": surplus_val,
            "solar_curtailment_mw": curt_val,
            "battery_charge_mw": charge_val,
            "battery_discharge_mw": discharge_val,
            "residual_mw": residual_val
        })

    dispatch = pd.DataFrame(
        dispatch_rows,
        columns=[
            "timestamp", "solar_mw", "demand_mw", "solar_surplus_mw",
            "solar_curtailment_mw", "battery_charge_mw", "battery_discharge_mw",
            "residual_mw"
        ]
    )

    selected_sites = pd.DataFrame(
        selected,
        columns=["bus_id", "power_mw", "energy_mwh", "site_cost_factor"]
    )

    return {
        "selected_sites": selected_sites,
        "dispatch": dispatch,
        "objective_value": pyo.value(m.objective),
        "peak_residual_mw": pyo.value(m.peak)
    }
