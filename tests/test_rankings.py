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
    """Test ranking by ROI"""
    calcs = [
        _make_calc(1, "Low ROI", 100, 10, 12000),
        _make_calc(2, "High ROI", 500, 2, 60000),
        _make_calc(3, "Medium ROI", 300, 4, 36000),
    ]
    
    ranked = rank_by_roi(calcs, top=5)
    
    assert len(ranked) == 3
    assert ranked[0].process_name == "High ROI"
    assert ranked[1].process_name == "Medium ROI"
    assert ranked[2].process_name == "Low ROI"


def test_rank_by_roi_top_n():
    """Test ranking with top_n limit"""
    calcs = [
        _make_calc(i, f"Process {i}", i * 100, 10, i * 10000)
        for i in range(1, 6)
    ]
    
    ranked = rank_by_roi(calcs, top=3)
    
    assert len(ranked) == 3
    assert ranked[0].roi_percentage_first_year == 500
    assert ranked[1].roi_percentage_first_year == 400
    assert ranked[2].roi_percentage_first_year == 300


def test_rank_by_roi_empty():
    """Test ranking with empty list"""
    ranked = rank_by_roi([], top=5)
    assert ranked == []


def test_rank_by_payback():
    """Test ranking by payback period"""
    calcs = [
        _make_calc(1, "Long Payback", 100, 12, 12000),
        _make_calc(2, "Short Payback", 500, 1, 60000),
        _make_calc(3, "Medium Payback", 300, 6, 36000),
    ]
    
    ranked = rank_by_payback(calcs, top=5)
    
    assert len(ranked) == 3
    assert ranked[0].process_name == "Short Payback"
    assert ranked[1].process_name == "Medium Payback"
    assert ranked[2].process_name == "Long Payback"


def test_rank_by_payback_with_infinity():
    """Test ranking with infinite payback"""
    calcs = [
        _make_calc(1, "No Return", 0, float('inf'), 0),
        _make_calc(2, "Quick Return", 500, 2, 60000),
    ]
    
    ranked = rank_by_payback(calcs, top=5)
    
    # Should handle infinity gracefully
    assert len(ranked) == 2
    assert ranked[0].process_name == "Quick Return"


def test_rank_by_payback_top_n():
    """Test payback ranking with top_n limit"""
    calcs = [
        _make_calc(i, f"Process {i}", i * 100, i, i * 10000)
        for i in range(1, 6)
    ]
    
    ranked = rank_by_payback(calcs, top=2)
    
    assert len(ranked) == 2
    assert ranked[0].payback_period_months == 1
    assert ranked[1].payback_period_months == 2


def test_rank_by_payback_empty():
    """Test payback ranking with empty list"""
    ranked = rank_by_payback([], top=5)
    assert ranked == []


def test_rank_by_annual_savings():
    """Test ranking by annual savings"""
    calcs = [
        _make_calc(1, "Low Savings", 100, 10, 12000),
        _make_calc(2, "High Savings", 500, 2, 60000),
        _make_calc(3, "Medium Savings", 300, 4, 36000),
    ]
    
    ranked = rank_by_annual_savings(calcs, top=5)
    
    assert len(ranked) == 3
    assert ranked[0].process_name == "High Savings"
    assert ranked[1].process_name == "Medium Savings"
    assert ranked[2].process_name == "Low Savings"


def test_rank_by_annual_savings_top_n():
    """Test savings ranking with top_n limit"""
    calcs = [
        _make_calc(i, f"Process {i}", i * 100, 10, i * 10000)
        for i in range(1, 6)
    ]
    
    ranked = rank_by_annual_savings(calcs, top=3)
    
    assert len(ranked) == 3
    assert ranked[0].annual_savings == 50000
    assert ranked[1].annual_savings == 40000
    assert ranked[2].annual_savings == 30000


def test_rank_by_annual_savings_empty():
    """Test savings ranking with empty list"""
    ranked = rank_by_annual_savings([], top=5)
    assert ranked == []


def test_rank_by_roi_with_negative_roi():
    """Test ranking with negative ROI values"""
    calcs = [
        _make_calc(1, "Negative ROI", -50, 100, -5000),
        _make_calc(2, "Positive ROI", 100, 10, 12000),
    ]
    
    ranked = rank_by_roi(calcs, top=5)
    
    assert len(ranked) == 2
    assert ranked[0].roi_percentage_first_year == 100
    assert ranked[1].roi_percentage_first_year == -50


def test_rank_all_functions_same_data():
    """Test all ranking functions on same data"""
    calcs = [
        _make_calc(1, "Process A", 200, 8, 25000),
        _make_calc(2, "Process B", 400, 3, 50000),
        _make_calc(3, "Process C", 150, 6, 18000),
    ]
    
    roi_ranked = rank_by_roi(calcs, top=5)
    payback_ranked = rank_by_payback(calcs, top=5)
    savings_ranked = rank_by_annual_savings(calcs, top=5)
    
    # Different ranking functions produce different orders
    assert roi_ranked[0].process_name == "Process B"  # Highest ROI
    assert payback_ranked[0].process_name == "Process B"  # Lowest payback
    assert savings_ranked[0].process_name == "Process B"  # Highest savings

