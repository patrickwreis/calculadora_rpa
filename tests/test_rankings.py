# -*- coding: utf-8 -*-
"""Unit tests for ranking utilities."""
from datetime import datetime
from src.analysis.ranking import rank_by_roi, rank_by_payback, rank_by_annual_savings
from src.models.calculation import Calculation


def _make_calc(id, name, roi, payback, annual):
    return Calculation(
        id=id,
        process_name=name,
        current_time_per_month=100,
        people_involved=1,
        hourly_rate=10,
        rpa_implementation_cost=1000,
        rpa_monthly_cost=10,
        expected_automation_percentage=50,
        monthly_savings=annual / 12 if annual is not None else 0,
        annual_savings=annual,
        payback_period_months=payback,
        roi_first_year=roi / 100 * 1000,
        roi_percentage_first_year=roi,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


def test_rank_by_roi():
    a = _make_calc(1, "A", 10, 6, 12000)
    b = _make_calc(2, "B", 50, 12, 6000)
    c = _make_calc(3, "C", 30, 3, 20000)
    ranked = rank_by_roi([a, b, c], top=3)
    assert [r.process_name for r in ranked] == ["B", "C", "A"]


def test_rank_by_payback():
    a = _make_calc(1, "A", 10, 6, 12000)
    b = _make_calc(2, "B", 50, float('inf'), 6000)
    c = _make_calc(3, "C", 30, 3, 20000)
    ranked = rank_by_payback([a, b, c], top=3)
    assert [r.process_name for r in ranked] == ["C", "A", "B"]


def test_rank_by_annual_savings():
    a = _make_calc(1, "A", 10, 6, 12000)
    b = _make_calc(2, "B", 50, 12, 6000)
    c = _make_calc(3, "C", 30, 3, 20000)
    ranked = rank_by_annual_savings([a, b, c], top=2)
    assert [r.process_name for r in ranked] == ["C", "A"]
