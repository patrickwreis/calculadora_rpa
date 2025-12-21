# -*- coding: utf-8 -*-
"""Tests for calculator utilities"""
import pytest
from src.calculator.utils import format_currency, format_percentage, format_months, validate_input


class TestFormatCurrency:
    """Test currency formatting"""
    
    def test_format_currency_brl(self):
        """Test BRL currency formatting"""
        result = format_currency(1000.00)
        assert result == "R$ 1.000,00"
    
    def test_format_currency_brl_with_decimals(self):
        """Test BRL formatting with decimals"""
        result = format_currency(1234.56)
        assert result == "R$ 1.234,56"
    
    def test_format_currency_brl_zero(self):
        """Test BRL formatting with zero"""
        result = format_currency(0)
        assert result == "R$ 0,00"
    
    def test_format_currency_brl_negative(self):
        """Test BRL formatting with negative value"""
        result = format_currency(-1000.00)
        assert result == "R$ -1.000,00"
    
    def test_format_currency_usd(self):
        """Test USD currency formatting"""
        result = format_currency(1000.00, currency="USD")
        assert result == "$1,000.00"
    
    def test_format_currency_usd_decimals(self):
        """Test USD formatting with decimals"""
        result = format_currency(1234.56, currency="USD")
        assert result == "$1,234.56"
    
    def test_format_currency_large_number(self):
        """Test formatting large numbers"""
        result = format_currency(1000000.00)
        assert result == "R$ 1.000.000,00"


class TestFormatPercentage:
    """Test percentage formatting"""
    
    def test_format_percentage_default(self):
        """Test default percentage formatting"""
        result = format_percentage(50.5)
        assert result == "50.50%"
    
    def test_format_percentage_zero(self):
        """Test zero percentage"""
        result = format_percentage(0)
        assert result == "0.00%"
    
    def test_format_percentage_one_decimal(self):
        """Test percentage with 1 decimal place"""
        result = format_percentage(50.567, decimals=1)
        assert result == "50.6%"
    
    def test_format_percentage_no_decimals(self):
        """Test percentage with no decimal places"""
        result = format_percentage(50.567, decimals=0)
        assert result == "51%"
    
    def test_format_percentage_negative(self):
        """Test negative percentage"""
        result = format_percentage(-50.50)
        assert result == "-50.50%"
    
    def test_format_percentage_large(self):
        """Test large percentage"""
        result = format_percentage(999.999)
        # Should format with 2 decimals - may round to 1000.00%
        assert "%" in result and ("999" in result or "1000" in result)


class TestFormatMonths:
    """Test month formatting"""
    
    def test_format_months_single_month(self):
        """Test formatting single month"""
        result = format_months(1)
        assert "1" in result and "m" in result  # Contains 1 and 'm' for month
    
    def test_format_months_multiple_months(self):
        """Test formatting multiple months"""
        result = format_months(6)
        # Should contain 6 and 'm' for months
        assert "6" in result and "m" in result
    
    def test_format_months_single_year(self):
        """Test formatting single year"""
        result = format_months(12)
        assert result == "1 ano"
    
    def test_format_months_multiple_years(self):
        """Test formatting multiple years"""
        result = format_months(24)
        assert result == "2 anos"
    
    def test_format_months_year_and_months(self):
        """Test formatting year and months combined"""
        result = format_months(13)
        assert result == "1a 1m"
    
    def test_format_months_years_and_months(self):
        """Test formatting multiple years and months"""
        result = format_months(26)
        assert result == "2a 2m"
    
    def test_format_months_zero(self):
        """Test formatting zero months"""
        result = format_months(0)
        # Should contain 0 and 'm' for months
        assert "0" in result and "m" in result
    
    def test_format_months_infinity(self):
        """Test formatting infinite payback"""
        result = format_months(float('inf'))
        assert result == "Indefinido"
    
    def test_format_months_decimal(self):
        """Test formatting decimal months"""
        result = format_months(6.5)
        # Should contain 6 and 'm' for months
        assert "6" in result and "m" in result


class TestValidateInput:
    """Test input validation"""
    
    @pytest.fixture
    def valid_input(self):
        """Valid input data"""
        return {
            'process_name': 'Test Process',
            'current_time_per_month': 40,
            'people_involved': 2,
            'hourly_rate': 100,
            'rpa_implementation_cost': 10000,
            'rpa_monthly_cost': 500,
            'expected_automation_percentage': 80,
        }
    
    def test_validate_input_valid(self, valid_input):
        """Test validation with valid data"""
        is_valid, message = validate_input(valid_input)
        assert is_valid is True
        assert message == ""
    
    def test_validate_input_missing_field(self, valid_input):
        """Test validation with missing required field"""
        del valid_input['process_name']
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "process_name" in message
    
    def test_validate_input_all_required_fields(self, valid_input):
        """Test that all required fields are checked"""
        for field in valid_input.keys():
            test_data = valid_input.copy()
            del test_data[field]
            is_valid, message = validate_input(test_data)
            assert is_valid is False, f"Should fail when {field} is missing"
    
    def test_validate_input_current_time_negative(self, valid_input):
        """Test validation with negative hours"""
        valid_input['current_time_per_month'] = -1
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "Tempo atual" in message or "current_time" in message.lower()
    
    def test_validate_input_people_zero(self, valid_input):
        """Test validation with zero people"""
        valid_input['people_involved'] = 0
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "Pessoas" in message or "people" in message.lower()
    
    def test_validate_input_people_too_many(self, valid_input):
        """Test validation with too many people"""
        valid_input['people_involved'] = 10001
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "Pessoas" in message or "people" in message.lower()
    
    def test_validate_input_hourly_rate_negative(self, valid_input):
        """Test validation with negative hourly rate"""
        valid_input['hourly_rate'] = -50
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "horária" in message or "hourly" in message.lower()
    
    def test_validate_input_cost_negative(self, valid_input):
        """Test validation with negative cost"""
        valid_input['rpa_implementation_cost'] = -5000
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "implementação" in message or "implementation" in message.lower()
    
    def test_validate_input_automation_percentage_below_zero(self, valid_input):
        """Test validation with percentage below 0"""
        valid_input['expected_automation_percentage'] = -1
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "automação" in message or "automation" in message.lower()
    
    def test_validate_input_automation_percentage_above_100(self, valid_input):
        """Test validation with percentage above 100"""
        valid_input['expected_automation_percentage'] = 101
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "automação" in message or "automation" in message.lower()
    
    def test_validate_input_non_numeric_field(self, valid_input):
        """Test validation with non-numeric value"""
        valid_input['hourly_rate'] = "not_a_number"
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
        assert "horária" in message or "hourly" in message.lower() or "número" in message.lower()
    
    def test_validate_input_none_value(self, valid_input):
        """Test validation with None value"""
        valid_input['hourly_rate'] = None
        is_valid, message = validate_input(valid_input)
        assert is_valid is False
    
    def test_validate_input_with_extra_fields(self, valid_input):
        """Test validation ignores extra fields"""
        valid_input['extra_field'] = 'should_be_ignored'
        is_valid, message = validate_input(valid_input)
        assert is_valid is True
    
    def test_validate_input_boundary_automation_0(self, valid_input):
        """Test validation with automation percentage at 0 boundary"""
        valid_input['expected_automation_percentage'] = 0
        is_valid, message = validate_input(valid_input)
        assert is_valid is True
    
    def test_validate_input_boundary_automation_100(self, valid_input):
        """Test validation with automation percentage at 100 boundary"""
        valid_input['expected_automation_percentage'] = 100
        is_valid, message = validate_input(valid_input)
        assert is_valid is True
