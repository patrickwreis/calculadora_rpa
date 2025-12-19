"""Ranking utilities for saved calculations.

Provides simple ranking functions to order saved `Calculation` records
by ROI, payback (shorter is better) and annual savings.
"""
from typing import List
from math import inf
from src.models.calculation import Calculation


def _safe_payback(calc: Calculation) -> float:
    """Return a numeric payback value where infinite/None become +inf for sorting."""
    v = getattr(calc, "payback_period_months", None)
    if v is None:
        return inf
    try:
        return float(v)
    except Exception:
        return inf


def rank_by_roi(calculations: List[Calculation], top: int = 5) -> List[Calculation]:
    """Return top calculations sorted by `roi_percentage_first_year` (desc)."""
    return sorted(
        calculations,
        key=lambda c: getattr(c, "roi_percentage_first_year", 0) or 0,
        reverse=True,
    )[:top]


def rank_by_payback(calculations: List[Calculation], top: int = 5) -> List[Calculation]:
    """Return top calculations sorted by `payback_period_months` (asc).

    Calculations with infinite payback are placed at the end.
    """
    return sorted(calculations, key=_safe_payback)[:top]


def rank_by_annual_savings(calculations: List[Calculation], top: int = 5) -> List[Calculation]:
    """Return top calculations sorted by `annual_savings` (desc)."""
    return sorted(
        calculations,
        key=lambda c: getattr(c, "annual_savings", 0) or 0,
        reverse=True,
    )[:top]
