# -*- coding: utf-8 -*-
"""Tests for process classification logic"""
import pytest
from src.models.calculation import classify_process


class TestProcessClassification:
    """Test classification logic based on ROI and payback period"""
    
    def test_quick_win_high_roi_short_payback(self):
        """Test QUICK WIN: ROI > 50% AND Payback < 12 months"""
        assert classify_process(roi_percentage=100, payback_months=6) == "QUICK WIN"
        assert classify_process(roi_percentage=75, payback_months=11) == "QUICK WIN"
        assert classify_process(roi_percentage=150, payback_months=1) == "QUICK WIN"
    
    def test_quick_win_boundary_roi(self):
        """Test QUICK WIN at ROI boundary (exactly 50%)"""
        # Should NOT be QUICK WIN if ROI is exactly 50% (needs > 50)
        assert classify_process(roi_percentage=50, payback_months=6) == "MÉDIO PRAZO"
        assert classify_process(roi_percentage=50.1, payback_months=6) == "QUICK WIN"
    
    def test_quick_win_boundary_payback(self):
        """Test QUICK WIN at payback boundary (exactly 12 months)"""
        # Should NOT be QUICK WIN if payback is exactly 12 (needs < 12)
        assert classify_process(roi_percentage=100, payback_months=12) == "MÉDIO PRAZO"
        assert classify_process(roi_percentage=100, payback_months=11.9) == "QUICK WIN"
    
    def test_medio_prazo_positive_roi_medium_payback(self):
        """Test MÉDIO PRAZO: ROI > 0% AND Payback < 24 months"""
        assert classify_process(roi_percentage=30, payback_months=18) == "MÉDIO PRAZO"
        assert classify_process(roi_percentage=5, payback_months=20) == "MÉDIO PRAZO"
        assert classify_process(roi_percentage=1, payback_months=23) == "MÉDIO PRAZO"
    
    def test_medio_prazo_boundary_roi(self):
        """Test MÉDIO PRAZO at ROI boundary (exactly 0%)"""
        # Should NOT be MÉDIO PRAZO if ROI is exactly 0% (needs > 0)
        assert classify_process(roi_percentage=0, payback_months=18) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=0.1, payback_months=18) == "MÉDIO PRAZO"
    
    def test_medio_prazo_boundary_payback(self):
        """Test MÉDIO PRAZO at payback boundary (exactly 24 months)"""
        # Should NOT be MÉDIO PRAZO if payback is exactly 24 (needs < 24)
        assert classify_process(roi_percentage=30, payback_months=24) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=30, payback_months=23.9) == "MÉDIO PRAZO"
    
    def test_baixa_prioridade_negative_roi(self):
        """Test BAIXA PRIORIDADE: ROI <= 0% OR Payback >= 24 months"""
        assert classify_process(roi_percentage=-10, payback_months=12) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=-50, payback_months=6) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=0, payback_months=12) == "BAIXA PRIORIDADE"
    
    def test_baixa_prioridade_long_payback(self):
        """Test BAIXA PRIORIDADE: Long payback period (>= 24 months)"""
        assert classify_process(roi_percentage=100, payback_months=24) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=100, payback_months=30) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=50, payback_months=25) == "BAIXA PRIORIDADE"
    
    def test_baixa_prioridade_both_poor_metrics(self):
        """Test BAIXA PRIORIDADE: Both ROI and payback are poor"""
        assert classify_process(roi_percentage=-10, payback_months=36) == "BAIXA PRIORIDADE"
        assert classify_process(roi_percentage=0, payback_months=48) == "BAIXA PRIORIDADE"
    
    def test_classification_with_zero_values(self):
        """Test classification with zero values"""
        # Zero ROI, short payback -> BAIXA PRIORIDADE (ROI must be > 0)
        assert classify_process(roi_percentage=0, payback_months=6) == "BAIXA PRIORIDADE"
        # Positive ROI, zero payback (unlikely but possible) -> QUICK WIN
        assert classify_process(roi_percentage=100, payback_months=0) == "QUICK WIN"
    
    def test_classification_with_large_values(self):
        """Test classification with very large values"""
        assert classify_process(roi_percentage=1000, payback_months=1) == "QUICK WIN"
        assert classify_process(roi_percentage=5000, payback_months=6) == "QUICK WIN"
    
    def test_classification_with_float_precision(self):
        """Test classification with float precision edge cases"""
        # Test with high precision floats
        assert classify_process(roi_percentage=50.00001, payback_months=11.99999) == "QUICK WIN"
        assert classify_process(roi_percentage=49.99999, payback_months=11.99999) == "MÉDIO PRAZO"
        assert classify_process(roi_percentage=50.00001, payback_months=12.00001) == "MÉDIO PRAZO"
    
    def test_classification_returns_string(self):
        """Test that classification always returns a string"""
        result = classify_process(100, 6)
        assert isinstance(result, str)
        
        result = classify_process(0, 24)
        assert isinstance(result, str)
        
        result = classify_process(-10, 36)
        assert isinstance(result, str)
    
    def test_valid_classification_values(self):
        """Test that only valid classification values are returned"""
        valid_classifications = {"QUICK WIN", "MÉDIO PRAZO", "BAIXA PRIORIDADE"}
        
        test_cases = [
            (100, 6),
            (50, 18),
            (0, 30),
            (-10, 12),
            (75, 24),
            (1, 1),
            (1000, 48),
        ]
        
        for roi, payback in test_cases:
            classification = classify_process(roi, payback)
            assert classification in valid_classifications, \
                f"Invalid classification '{classification}' for ROI={roi}, Payback={payback}"


class TestClassificationIntegration:
    """Integration tests for classification with database operations"""
    
    def test_classification_in_calculation_repr(self):
        """Test that classification appears in Calculation repr"""
        from src.models import Calculation
        
        calc = Calculation(
            process_name="Test Process",
            people_involved=2,
            current_time_per_month=100,
            hourly_rate=50,
            expected_automation_percentage=80,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=100,
            monthly_savings=500,
            annual_savings=6000,
            payback_period_months=10,
            roi_first_year=200,
            roi_percentage_first_year=100,
            classification="QUICK WIN",
            user_id=1
        )
        
        repr_str = repr(calc)
        assert "classification='QUICK WIN'" in repr_str
        assert "user_id=1" in repr_str
