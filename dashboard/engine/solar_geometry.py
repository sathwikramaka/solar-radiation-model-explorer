"""Solar geometry and the study's sunshine-based Angstrom-Prescott reference."""
import numpy as np

from .config import GSC, A_AP, B_AP


def day_length_and_ra(day_of_year, latitude_deg):
    """Return N (maximum sunshine hours) and Ra (extraterrestrial radiation, MJ m-2 d-1).

    The primary analysis uses the 0.003 coefficient printed in the study's
    cited solar-geometry equation. Keep this helper aligned with the notebook.
    """
    J = np.asarray(day_of_year, float)
    phi = np.radians(latitude_deg)
    dr = 1 + 0.003 * np.cos(2 * np.pi * J / 365)              # primary-study Earth-Sun distance factor
    delta = 0.409 * np.sin(2 * np.pi * J / 365 - 1.39)        # solar declination
    ws = np.arccos(-np.tan(phi) * np.tan(delta))              # sunset hour angle
    N = 24 * ws / np.pi
    Ra = (24 * 60 / np.pi) * GSC * dr * (ws * np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.sin(ws))
    return N, Ra


def angstrom_prescott(ssh, N, Ra):
    """Reference Rs = (a + b n/N) Ra, only where 0 <= n <= N (otherwise NaN; nothing is clipped)."""
    ssh, N, Ra = (np.asarray(x, float) for x in (ssh, N, Ra))
    with np.errstate(invalid="ignore"):
        valid = ~np.isnan(ssh) & (ssh >= 0) & (ssh <= N)
        return np.where(valid, (A_AP + B_AP * ssh / N) * Ra, np.nan)
