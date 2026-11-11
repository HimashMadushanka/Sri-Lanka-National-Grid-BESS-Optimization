import requests
import pandas as pd
from pathlib import Path


def download_nasa_power(
    latitude,
    longitude,
    start_date,
    end_date,
    output_path
):

    url = (
        "https://power.larc.nasa.gov/api/temporal/"
        "hourly/point"
    )

    parameters = {
        "parameters": "ALLSKY_SFC_SW_DWN,T2M",
        "community": "RE",
        "longitude": longitude,
        "latitude": latitude,
        "start": start_date,
        "end": end_date,
        "format": "JSON",
        "time-standard": "UTC"
    }

    response = requests.get(
        url, params=parameters, timeout=120
    )

    response.raise_for_status()

    result = response.json()

    parameter_data = result["properties"]["parameter"]

    solar = parameter_data["ALLSKY_SFC_SW_DWN"]
    temperature = parameter_data["T2M"]

    df = pd.DataFrame({
        "timestamp": pd.to_datetime(
            list(solar.keys()),
            format="%Y%m%d%H",
            utc=True
        ),
        "solar_irradiance": list(solar.values()),
        "temperature_c": list(temperature.values())
    })

    df["solar_irradiance"] = pd.to_numeric(
        df["solar_irradiance"], errors="coerce"
    )

    df["temperature_c"] = pd.to_numeric(
        df["temperature_c"], errors="coerce"
    )

    df.to_csv(output_path, index=False)

    print(f"Downloaded NASA data: {output_path}")

    return df