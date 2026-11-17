import networkx as nx
import pandas as pd


def calculate_graph_metrics(graph):
    """Return standard centrality and degree measures for each grid bus."""
    nodes = list(graph.nodes)
    betweenness = nx.betweenness_centrality(graph, normalized=True)
    closeness = nx.closeness_centrality(graph)
    degree_centrality = nx.degree_centrality(graph) if len(nodes) > 1 else {
        node: 0.0 for node in nodes
    }

    return pd.DataFrame([
        {
            "bus_id": str(node),
            "degree": int(graph.degree[node]),
            "degree_centrality": degree_centrality[node],
            "betweenness_centrality": betweenness[node],
            "closeness_centrality": closeness[node],
        }
        for node in nodes
    ], columns=[
        "bus_id", "degree", "degree_centrality",
        "betweenness_centrality", "closeness_centrality",
    ])


def add_solar_distance(graph, metrics, solar_plants):
    """Add each bus's nearest solar plant distance in kilometers."""
    result = metrics.copy()
    result["solar_distance_km"] = float("nan")
    if result.empty or solar_plants.empty:
        return result

    required = {"latitude", "longitude"}
    if not required.issubset(solar_plants.columns):
        return result

    plant_coordinates = solar_plants[["latitude", "longitude"]].apply(
        pd.to_numeric, errors="coerce"
    ).dropna().to_numpy()
    if not len(plant_coordinates):
        return result

    def haversine_km(lat1, lon1, lat2, lon2):
        from math import asin, cos, radians, sin, sqrt

        lat1, lon1, lat2, lon2 = map(radians, (lat1, lon1, lat2, lon2))
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
        return 6371.0 * 2 * asin(sqrt(min(1.0, a)))

    for index, row in result.iterrows():
        attributes = graph.nodes.get(str(row["bus_id"]), {})
        try:
            latitude = float(attributes["latitude"])
            longitude = float(attributes["longitude"])
        except (KeyError, TypeError, ValueError):
            continue
        distances = [
            haversine_km(latitude, longitude, plant_lat, plant_lon)
            for plant_lat, plant_lon in plant_coordinates
        ]
        result.at[index, "solar_distance_km"] = min(distances)

    result["distance_to_solar_km"] = result["solar_distance_km"]
    return result


def rank_candidates(
    metrics,
    centrality_weight=0.5,
    solar_distance_weight=0.5,
):
    """Score substations, favoring central nodes close to solar plants."""
    if centrality_weight < 0 or solar_distance_weight < 0:
        raise ValueError("Candidate weights must be non-negative.")
    weight_total = centrality_weight + solar_distance_weight
    if weight_total <= 0:
        raise ValueError("At least one candidate weight must be positive.")

    result = metrics.copy()
    for column in (
        "bus_id", "voltage_kv", "degree", "betweenness_centrality",
    ):
        if column not in result.columns:
            result[column] = pd.Series(dtype="object" if column == "bus_id" else "float64")

    if "solar_distance_km" in result.columns:
        distance_column = "solar_distance_km"
    elif "distance_to_solar_km" in result.columns:
        distance_column = "distance_to_solar_km"
    else:
        distance_column = "solar_distance_km"
        result[distance_column] = float("nan")

    centrality = pd.to_numeric(
        result["betweenness_centrality"], errors="coerce"
    ).fillna(0.0)
    max_centrality = centrality.max() if not centrality.empty else 0.0
    centrality_score = centrality / max_centrality if max_centrality > 0 else centrality * 0

    distance = pd.to_numeric(result[distance_column], errors="coerce")
    finite_distance = distance.dropna()
    if finite_distance.empty:
        distance_score = pd.Series(0.0, index=result.index)
    else:
        max_distance = finite_distance.max()
        distance_score = (
            1.0 - distance / max_distance
            if max_distance > 0
            else pd.Series(1.0, index=result.index)
        ).fillna(0.0).clip(lower=0.0, upper=1.0)

    result["site_score"] = (
        centrality_weight * centrality_score
        + solar_distance_weight * distance_score
    ) / weight_total
    # Planning-level proxy only; replace with measured site costs when available.
    result["site_cost_factor"] = pd.to_numeric(
        result.get(
            "site_cost_factor",
            1.3 - 0.6 * result["site_score"],
        ),
        errors="coerce",
    ).fillna(1.0).clip(lower=0.7, upper=1.3)
    result["distance_to_solar_km"] = distance

    return result.sort_values(
        "site_score", ascending=False, kind="stable"
    ).reset_index(drop=True)


def build_grid_graph(substations, transmission_lines):
    """Build an undirected transmission graph from substation and line tables."""
    required_substations = {"bus_id"}
    required_lines = {"from_bus", "to_bus"}

    missing_substations = required_substations - set(substations.columns)
    missing_lines = required_lines - set(transmission_lines.columns)
    if missing_substations:
        raise ValueError(
            f"Substations are missing columns: {sorted(missing_substations)}"
        )
    if missing_lines:
        raise ValueError(
            f"Transmission lines are missing columns: {sorted(missing_lines)}"
        )

    graph = nx.Graph()

    for _, row in substations.iterrows():
        attributes = row.drop(labels=["bus_id"]).dropna().to_dict()
        graph.add_node(str(row["bus_id"]), **attributes)

    for _, row in transmission_lines.iterrows():
        attributes = row.drop(labels=["from_bus", "to_bus"]).dropna().to_dict()
        graph.add_edge(
            str(row["from_bus"]),
            str(row["to_bus"]),
            **attributes,
        )

    return graph
