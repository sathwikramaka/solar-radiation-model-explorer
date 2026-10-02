"""Evaluation metrics (paper Table 3), copied from notebook Cell 9."""
import numpy as np


def calculate_metrics(estimate, reference):
    """R2 = 1 - SSE/SST (not clipped, can be negative); MBE is signed (positive = overestimate)."""
    estimate, reference = np.asarray(estimate, float), np.asarray(reference, float)
    error = estimate - reference
    return {"n": len(reference),
            "R2":   1 - np.sum(error**2) / np.sum((reference - reference.mean())**2),
            "RMSE": np.sqrt(np.mean(error**2)),
            "MAE":  np.mean(np.abs(error)),
            "MBE":  np.mean(error)}
