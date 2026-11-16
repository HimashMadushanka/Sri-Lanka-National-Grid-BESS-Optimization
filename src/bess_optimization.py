import pandas as pd
import pyomo.environ as pyo


def optimize_bess(profile, candidates, config):

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

    dt = config["optimization"]["time_step_hours"]

    surplus = (
        profile["solar_mw"] - profile["demand_mw"]
    ).clip(lower=0).tolist()

    deficit = (
        profile["demand_mw"] - profile["solar_mw"]
    ).clip(lower=0).tolist()

    battery = config["battery"]
    opt = config["optimization"]

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
        365 / opt["profile_days_represented"]
    )

    m = pyo.ConcreteModel()

    m.I = pyo.Set(initialize=sites)
    m.T = pyo.RangeSet(0, n - 1)

    # Binary site installation decisions
    m.build = pyo.Var(m.I, domain=pyo.Binary)

    # Battery capacities
    m.power = pyo.Var(m.I, domain=pyo.NonNegativeReals)
    m.energy = pyo.Var(m.I, domain=pyo.NonNegativeReals)

    # Dispatch variables
    m.charge = pyo.Var(m.I, m.T, domain=pyo.NonNegativeReals)
    m.discharge = pyo.Var(m.I, m.T, domain=pyo.NonNegativeReals)
    m.soc = pyo.Var(m.I, m.T, domain=pyo.NonNegativeReals)

    m.curtailment = pyo.Var(m.T, domain=pyo.NonNegativeReals)
    m.residual = pyo.Var(m.T, domain=pyo.NonNegativeReals)

    m.peak = pyo.Var(domain=pyo.NonNegativeReals)

    # Power limits
    def maximum_power_rule(m, i):
        return m.power[i] <= (
            battery["maximum_power_per_site_mw"] * m.build[i]
        )

    m.max_power = pyo.Constraint(
        m.I, rule=maximum_power_rule
    )

    def minimum_power_rule(m, i):
        return m.power[i] >= (
            battery["minimum_power_mw"] * m.build[i]
        )

    m.min_power = pyo.Constraint(
        m.I, rule=minimum_power_rule
    )

    # Battery energy capacity follows selected duration
    def duration_rule(m, i):
        return m.energy[i] == duration * m.power[i]

    m.duration = pyo.Constraint(m.I, rule=duration_rule)

    # Disable charge and discharge where no battery exists
    m.charge_limit = pyo.Constraint(
        m.I, m.T,
        rule=lambda m, i, t:
            m.charge[i, t] <= m.power[i]
    )

    m.discharge_limit = pyo.Constraint(
        m.I, m.T,
        rule=lambda m, i, t:
            m.discharge[i, t] <= m.power[i]
    )

    # SOC bounds
    m.soc_limit = pyo.Constraint(
        m.I, m.T,
        rule=lambda m, i, t:
            m.soc[i, t] <= m.energy[i]
    )

    # Cyclic energy balance
    def soc_balance_rule(m, i, t):

        previous = n - 1 if t == 0 else t - 1

        return m.soc[i, t] == (
            m.soc[i, previous]
            + eta_charge * m.charge[i, t] * dt
            - m.discharge[i, t] * dt / eta_discharge
        )

    m.soc_balance = pyo.Constraint(
        m.I, m.T, rule=soc_balance_rule
    )

    # Solar surplus = charging + curtailment
    m.solar_balance = pyo.Constraint(
        m.T,
        rule=lambda m, t:
            sum(m.charge[i, t] for i in m.I)
            + m.curtailment[t]
            == surplus[t]
    )

    # Residual load after BESS discharge
    m.load_balance = pyo.Constraint(
        m.T,
        rule=lambda m, t:
            sum(m.discharge[i, t] for i in m.I)
            + m.residual[t]
            == deficit[t]
    )

    # Peak residual demand
    m.peak_limit = pyo.Constraint(
        m.T,
        rule=lambda m, t: m.peak >= m.residual[t]
    )

    m.site_limit = pyo.Constraint(
        expr=sum(m.build[i] for i in m.I)
        <= battery["maximum_number_of_sites"]
    )

    m.total_power_limit = pyo.Constraint(
        expr=sum(m.power[i] for i in m.I)
        <= opt["maximum_total_power_mw"]
    )

    # Annualized capital and operating cost
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
            battery["annual_om_usd_per_kw_year"]
            * 1000 * m.power[i]
            for i in m.I
        )

        curtailment_cost = (
            annualization_scale
            * opt["curtailment_penalty_usd_per_mwh"]
            * sum(m.curtailment[t] * dt for t in m.T)
        )

        peak_benefit = (
            -opt["peak_reduction_value_usd_per_mw_year"]
            * (
                max(deficit)
                - m.peak
            )
        )

        return (
            annualized_investment
            + annual_om
            + curtailment_cost
            + peak_benefit
        )

    m.objective = pyo.Objective(
        rule=objective_rule,
        sense=pyo.minimize
    )

    solver = pyo.SolverFactory("appsi_highs")

    if not solver.available(exception_flag=False):
        raise RuntimeError(
            "HiGHS solver not found. Install highspy."
        )

    result = solver.solve(m, tee=True)

    condition = result.solver.termination_condition

    if condition != pyo.TerminationCondition.optimal:
        raise RuntimeError(
            f"Optimization not optimal: {condition}"
        )

    # Selected battery locations
    selected = []

    for i in sites:

        if pyo.value(m.build[i]) > 0.5:

            selected.append({
                "bus_id": i,
                "power_mw": pyo.value(m.power[i]),
                "energy_mwh": pyo.value(m.energy[i]),
                "site_cost_factor":
                    float(candidates.loc[
                        candidates["bus_id"].astype(str) == i,
                        "site_cost_factor"
                    ].iloc[0])
            })

    # Dispatch results
    dispatch_rows = []

    for t in range(n):

        charge = sum(
            pyo.value(m.charge[i, t]) for i in sites
        )

        discharge = sum(
            pyo.value(m.discharge[i, t]) for i in sites
        )

        dispatch_rows.append({
            "timestamp": profile.loc[t, "timestamp"] if "timestamp" in profile.columns else t,
            "solar_mw": profile.loc[t, "solar_mw"],
            "demand_mw": profile.loc[t, "demand_mw"],
            "solar_surplus_mw": surplus[t],
            "solar_curtailment_mw": pyo.value(m.curtailment[t]),
            "battery_charge_mw": charge,
            "battery_discharge_mw": discharge,
            "residual_mw": pyo.value(m.residual[t])
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