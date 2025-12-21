# -*- coding: utf-8 -*-
"""Tests for automation metrics calculation"""
import pytest
from src.calculator.utils import calculate_automation_metrics


class TestAutomationMetrics:
    """Test automation metrics calculation with exception rates"""
    
    def test_no_exceptions_high_automation(self):
        """Test 100% automation with 0% exceptions"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=100,
            exception_rate=0
        )
        
        assert metrics["fully_automated_pct"] == 100.0
        assert metrics["partial_review_pct"] == 0.0
        assert metrics["still_manual_pct"] == 0.0
        assert metrics["total_manual_effort_pct"] == 0.0
    
    def test_partial_automation_no_exceptions(self):
        """Test 80% automation with 0% exceptions"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=80,
            exception_rate=0
        )
        
        assert metrics["fully_automated_pct"] == 80.0
        assert metrics["partial_review_pct"] == 0.0
        assert metrics["still_manual_pct"] == 20.0
        assert metrics["total_manual_effort_pct"] == 20.0
    
    def test_automation_with_exceptions(self):
        """Test 80% automation with 20% exceptions"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=80,
            exception_rate=20
        )
        
        # 80% × (1 - 20%) = 64%
        assert metrics["fully_automated_pct"] == 64.0
        # 80% × 20% = 16%
        assert metrics["partial_review_pct"] == 16.0
        # 100% - 80% = 20%
        assert metrics["still_manual_pct"] == 20.0
        # 16% + 20% = 36%
        assert metrics["total_manual_effort_pct"] == 36.0
    
    def test_high_automation_high_exceptions(self):
        """Test 90% automation with 50% exceptions"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=90,
            exception_rate=50
        )
        
        # 90% × (1 - 50%) = 45%
        assert metrics["fully_automated_pct"] == 45.0
        # 90% × 50% = 45%
        assert metrics["partial_review_pct"] == 45.0
        # 100% - 90% = 10%
        assert metrics["still_manual_pct"] == 10.0
        # 45% + 10% = 55%
        assert metrics["total_manual_effort_pct"] == 55.0
    
    def test_low_automation_low_exceptions(self):
        """Test 50% automation with 10% exceptions"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=50,
            exception_rate=10
        )
        
        # 50% × (1 - 10%) = 45%
        assert metrics["fully_automated_pct"] == 45.0
        # 50% × 10% = 5%
        assert metrics["partial_review_pct"] == 5.0
        # 100% - 50% = 50%
        assert metrics["still_manual_pct"] == 50.0
        # 5% + 50% = 55%
        assert metrics["total_manual_effort_pct"] == 55.0
    
    def test_zero_automation(self):
        """Test 0% automation (no change)"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=0,
            exception_rate=10  # Exception rate ignored if nothing automated
        )
        
        assert metrics["fully_automated_pct"] == 0.0
        assert metrics["partial_review_pct"] == 0.0
        assert metrics["still_manual_pct"] == 100.0
        assert metrics["total_manual_effort_pct"] == 100.0
    
    def test_high_exceptions_on_partial_automation(self):
        """Test 70% automation with 80% exceptions (high manual review)"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=70,
            exception_rate=80
        )
        
        # 70% × (1 - 80%) = 14%
        assert abs(metrics["fully_automated_pct"] - 14.0) < 0.001
        # 70% × 80% = 56%
        assert abs(metrics["partial_review_pct"] - 56.0) < 0.001
        # 100% - 70% = 30%
        assert abs(metrics["still_manual_pct"] - 30.0) < 0.001
        # 56% + 30% = 86%
        assert abs(metrics["total_manual_effort_pct"] - 86.0) < 0.001
    
    def test_realistic_scenario_medium_risk(self):
        """Test realistic scenario: 75% can be automated, 25% needs review"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=75,
            exception_rate=25
        )
        
        # 75% × (1 - 25%) = 56.25%
        assert metrics["fully_automated_pct"] == 56.25
        # 75% × 25% = 18.75%
        assert metrics["partial_review_pct"] == 18.75
        # 100% - 75% = 25%
        assert metrics["still_manual_pct"] == 25.0
        # 18.75% + 25% = 43.75%
        assert metrics["total_manual_effort_pct"] == 43.75
    
    def test_boundary_100_percent_exceptions(self):
        """Test boundary: automation but all need manual review"""
        metrics = calculate_automation_metrics(
            expected_automation_percentage=85,
            exception_rate=100
        )
        
        # 85% × (1 - 100%) = 0%
        assert metrics["fully_automated_pct"] == 0.0
        # 85% × 100% = 85%
        assert metrics["partial_review_pct"] == 85.0
        # 100% - 85% = 15%
        assert metrics["still_manual_pct"] == 15.0
        # 85% + 15% = 100%
        assert metrics["total_manual_effort_pct"] == 100.0
    
    def test_percentages_sum_to_100(self):
        """Test that all components sum to 100%"""
        test_cases = [
            (100, 0),
            (80, 20),
            (75, 25),
            (50, 50),
            (0, 100),
            (90, 10),
        ]
        
        for automation, exceptions in test_cases:
            metrics = calculate_automation_metrics(automation, exceptions)
            total = (metrics["fully_automated_pct"] + 
                    metrics["partial_review_pct"] + 
                    metrics["still_manual_pct"])
            assert abs(total - 100.0) < 0.001, \
                f"Metrics don't sum to 100 for automation={automation}%, exception={exceptions}%"
    
    def test_returns_dict_with_all_keys(self):
        """Test that function returns dict with all required keys"""
        metrics = calculate_automation_metrics(80, 20)
        
        required_keys = {
            "fully_automated_pct",
            "partial_review_pct",
            "still_manual_pct",
            "total_manual_effort_pct"
        }
        
        assert set(metrics.keys()) == required_keys
    
    def test_all_values_are_floats(self):
        """Test that all returned values are floats"""
        metrics = calculate_automation_metrics(75, 15)
        
        for key, value in metrics.items():
            assert isinstance(value, float), f"Key {key} is not a float"
    
    def test_all_values_non_negative(self):
        """Test that all percentages are non-negative"""
        test_cases = [
            (100, 100),
            (50, 50),
            (25, 75),
        ]
        
        for automation, exceptions in test_cases:
            metrics = calculate_automation_metrics(automation, exceptions)
            for key, value in metrics.items():
                assert value >= 0, f"{key} is negative: {value}"
                assert value <= 100, f"{key} exceeds 100: {value}"

