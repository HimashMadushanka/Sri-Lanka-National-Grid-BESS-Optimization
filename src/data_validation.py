import pandas as pd
import numpy as np

REQUIRED_COLUMNS = {
    "grid_substations": [
        "bus_id", "name", "latitude", "longitude", "voltage_kv"
    ],
    "transmission_lines": [
        "line_id", "from_bus", "to_bus", "length_km"
    ],
    "solar_plants": [
        "plant_id", "name", "bus_id", "latitude",
        "longitude", "capacity_mw"
    ],
    "system_hourly_profile": [
        "timestamp", "demand_mw", "solar_mw"
    ]
}

def read_and_validate(path, dataset_name):
    df = pd.read_csv(path)

    required = REQUIRED_COLUMNS[dataset_name]

    missing = set(required) - set(df.columns)

    if missing:
        raise ValueError(
            f"{dataset_name} is missing columns: {missing}"
        )

    if df.empty:
        raise ValueError(
            f"{dataset_name} contains no records."
        )

    return df


def clean_hourly_profile(df):

    data = df.copy()

    data["timestamp"] = pd.to_datetime(
        data["timestamp"], errors="coerce", utc=True
    )

    data["demand_mw"] = pd.to_numeric(
        data["demand_mw"], errors="coerce"
    )

    data["solar_mw"] = pd.to_numeric(
        data["solar_mw"], errors="coerce"
    )

    data = data.dropna(
        subset=["timestamp", "demand_mw", "solar_mw"]
    )

    if (data[["demand_mw", "solar_mw"]] < 0).any().any():
        raise ValueError("Negative demand or solar generation found.")

    data = data.groupby("timestamp", as_index=False)[
        ["demand_mw", "solar_mw"]
    ].mean()

    data = data.sort_values("timestamp").reset_index(drop=True)

    return data


def validate_grid(substations, lines):

    bus_ids = set(substations["bus_id"].astype(str))

    lines = lines.copy()
    lines["from_bus"] = lines["from_bus"].astype(str)
    lines["to_bus"] = lines["to_bus"].astype(str)

    invalid = lines[
        ~lines["from_bus"].isin(bus_ids)
        | ~lines["to_bus"].isin(bus_ids)
    ]

    if not invalid.empty:
        raise ValueError(
            f"{len(invalid)} transmission lines refer to unknown buses."
        )

    if (pd.to_numeric(lines["length_km"], errors="coerce") <= 0).any():
        raise ValueError("Transmission line lengths must be positive.")

    return True