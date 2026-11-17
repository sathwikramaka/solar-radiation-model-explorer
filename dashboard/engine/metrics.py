"""Evaluation metrics (paper Table 3), kept identical to the notebook's metrics()."""
import numpy as np


def calculate_metrics(estimate, reference):
    """R2 = squared Pearson correlation r^2 (always 0..1, as tabulated in the paper's Table 4).

    MBE is signed (positive = overestimate). 1 - SSE/SST is not used: it turns negative for any
    strongly biased model and is only reported as a sensitivity by the notebook.
    """
    estimate, reference = np.asarray(estimate, float), np.asarray(reference, float)
    if len(reference) == 0:
        return {"n": 0, "R2": np.nan, "RMSE": np.nan, "MAE": np.nan, "MBE": np.nan}
    error = estimate - reference
    r = np.corrcoef(estimate, reference)[0, 1] if len(reference) > 1 else np.nan
    return {"n": len(reference),
            "R2":   r * r,
            "RMSE": np.sqrt(np.mean(error**2)),
            "MAE":  np.mean(np.abs(error)),
            "MBE":  np.mean(error)}
