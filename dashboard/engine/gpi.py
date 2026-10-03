"""Literal GPI implementation from Karale et al. (2026), section 2.3.1."""
ALPHA = {"R2": -1, "RMSE": 1, "MAE": 1, "MBE": 1}


def calculate_gpi(table):
    """Min-max scale each indicator; constant indicators contribute zero; ties share rank.

    The paper's printed +1 direction for signed MBE is retained. This rewards lower signed
    bias (including negative bias); the README documents the conflict with its prose.
    """
    table = table.copy()
    table["GPI"] = 0.0
    for indicator, direction in ALPHA.items():
        values = table[indicator]
        span = values.max() - values.min()
        scaled = (values - values.min()) / span if span > 0 else values * 0 + 0.5
        table[f"y_{indicator}"] = scaled
        table[f"median_y_{indicator}"] = scaled.median()
        table["GPI"] += direction * (scaled.median() - scaled)
    table["rank"] = table.GPI.round(10).rank(ascending=False, method="min").astype("Int64")
    return table.sort_values(["rank", "model"], kind="stable")
