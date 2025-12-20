# -*- coding: utf-8 -*-
"""Tests for Input Validation"""
import pytest
from src.calculator.utils import InputValidator, ValidationError


class TestInputValidator:
    """Test suite for InputValidator class"""
    
    def test_validate_percentage_valid(self):
        """Test valid percentage validation"""
        is_valid, error = InputValidator.validate_percentage(50.0, "Test")
        assert is_valid is True
        assert error is None
    
    def test_validate_percentage_zero_allowed(self):
        """Test percentage validation with zero allowed"""
        is_valid, error = InputValidator.validate_percentage(0.0, "Test", allow_zero=True)
        assert is_valid is True
        assert error is None
    
    def test_validate_percentage_zero_not_allowed(self):
        """Test percentage validation with zero not allowed"""
        is_valid, error = InputValidator.validate_percentage(0.0, "Test", allow_zero=False)
        assert is_valid is False
        assert "Test" in error
    
    def test_validate_percentage_over_100(self):
        """Test percentage validation over 100%"""
        is_valid, error = InputValidator.validate_percentage(101.0, "Test")
        assert is_valid is False
        assert "100%" in error
    
    def test_validate_percentage_negative(self):
        """Test percentage validation with negative value"""
        is_valid, error = InputValidator.validate_percentage(-1.0, "Test")
        assert is_valid is False
    
    def test_validate_positive_number_valid(self):
        """Test valid positive number"""
        is_valid, error = InputValidator.validate_positive_number(100.0, "Test")
        assert is_valid is True
        assert error is None
    
    def test_validate_positive_number_zero_allowed(self):
        """Test positive number with zero allowed"""
        is_valid, error = InputValidator.validate_positive_number(0.0, "Test", allow_zero=True)
        assert is_valid is True
    
    def test_validate_positive_number_zero_not_allowed(self):
        """Test positive number with zero not allowed"""
        is_valid, error = InputValidator.validate_positive_number(0.0, "Test", allow_zero=False)
        assert is_valid is False
    
    def test_validate_positive_number_negative(self):
        """Test positive number with negative value"""
        is_valid, error = InputValidator.validate_positive_number(-10.0, "Test")
        assert is_valid is False
    
    def test_validate_integer_range_valid(self):
        """Test valid integer range"""
        is_valid, error = InputValidator.validate_integer_range(5, "Test", 1, 10)
        assert is_valid is True
        assert error is None
    
    def test_validate_integer_range_below_min(self):
        """Test integer range below minimum"""
        is_valid, error = InputValidator.validate_integer_range(0, "Test", 1, 10)
        assert is_valid is False
        assert "1 e 10" in error
    
    def test_validate_integer_range_above_max(self):
        """Test integer range above maximum"""
        is_valid, error = InputValidator.validate_integer_range(11, "Test", 1, 10)
        assert is_valid is False
    
    def test_validate_cross_fields_valid(self):
        """Test valid cross-field validation"""
        is_valid, error = InputValidator.validate_cross_fields(
            error_rate=10.0,
            exception_rate=20.0,
            expected_automation_percentage=70.0
        )
        assert is_valid is True
        assert error is None
    
    def test_validate_cross_fields_error_exception_over_100(self):
        """Test cross-field validation with error + exception > 100%"""
        is_valid, error = InputValidator.validate_cross_fields(
            error_rate=60.0,
            exception_rate=50.0,
            expected_automation_percentage=50.0
        )
        assert is_valid is False
        assert "100%" in error
    
    def test_validate_cross_fields_automation_exceeds_limit(self):
        """Test cross-field validation with automation exceeding limit"""
        is_valid, error = InputValidator.validate_cross_fields(
            error_rate=10.0,
            exception_rate=30.0,
            expected_automation_percentage=80.0
        )
        assert is_valid is False
        assert "exceção" in error.lower()
    
    def test_validate_all_inputs_valid(self):
        """Test complete valid input validation"""
        data = {
            'process_name': 'Invoice Processing',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'error_rate': 5.0,
            'exception_rate': 10.0,
            'fines_avoided': 100.0,
            'sql_savings': 50.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_validate_all_inputs_missing_required(self):
        """Test validation with missing required fields"""
        data = {
            'process_name': 'Test',
            # Missing other required fields
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert len(errors) > 0
        assert any("obrigatório" in e for e in errors)
    
    def test_validate_all_inputs_empty_process_name(self):
        """Test validation with empty process name"""
        data = {
            'process_name': '   ',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert any("nome do processo" in e.lower() for e in errors)
    
    def test_validate_all_inputs_negative_values(self):
        """Test validation with negative values"""
        data = {
            'process_name': 'Test',
            'current_time_per_month': -10.0,  # Invalid
            'people_involved': 2,
            'hourly_rate': -50.0,  # Invalid
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert len(errors) >= 2
    
    def test_validate_all_inputs_invalid_percentages(self):
        """Test validation with invalid percentages"""
        data = {
            'process_name': 'Test',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 150.0,  # Invalid > 100
            'error_rate': -5.0,  # Invalid negative
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert len(errors) >= 2
    
    def test_validate_all_inputs_people_out_of_range(self):
        """Test validation with people count out of range"""
        data = {
            'process_name': 'Test',
            'current_time_per_month': 160.0,
            'people_involved': 0,  # Invalid < 1
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert any("pessoas envolvidas" in e.lower() for e in errors)
    
    def test_validate_all_inputs_cross_field_violation(self):
        """Test validation with cross-field violations"""
        data = {
            'process_name': 'Test',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 95.0,
            'error_rate': 10.0,
            'exception_rate': 20.0,  # automation 95% > max 80% (100 - 20)
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is False
        assert any("exceção" in e.lower() for e in errors)
    
    def test_validate_all_inputs_with_optional_fields(self):
        """Test validation with optional fields"""
        data = {
            'process_name': 'Test',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'fines_avoided': 500.0,
            'sql_savings': 300.0,
            'maintenance_percentage': 15.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(data)
        assert is_valid is True
        assert len(errors) == 0
