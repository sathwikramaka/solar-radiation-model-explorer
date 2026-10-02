"""Global Performance Indicator (paper section 2.3.1, Despotovic et al. 2015), copied from notebook Cell 10.

GPI_i = sum_j alpha_j * (median_j - y_ij), alpha = -1 for R2 and +1 for RMSE, MAE, MBE,
where y is each indicator scaled to 0-1 across the 16 models. Highest GPI = rank 1.
"""

ALPHA = {"R2": -1, "RMSE": +1, "MAE": +1, "MBE": +1}


def calculate_gpi(table):
    """table: one row per model with columns R2, RMSE, MAE, MBE. Returns it with GPI and rank, sorted by rank.

    If all models share the same value of an indicator, max == min and GPI is NaN (not patched).
    """
    table = table.copy()
    table["GPI"] = 0.0
    for indicator, sign in ALPHA.items():
        x = table[indicator]
        scaled = (x - x.min()) / (x.max() - x.min())          # 0-1 scaling across the 16 models
        table["y_" + indicator] = scaled
        table["median_y_" + indicator] = scaled.median()
        table["GPI"] += sign * (scaled.median() - scaled)
    table["rank"] = table.GPI.round(10).rank(ascending=False, method="min").astype("Int64")
    return table.sort_values("rank")
