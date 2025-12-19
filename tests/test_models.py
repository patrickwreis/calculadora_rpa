# -*- coding: utf-8 -*-
"""Tests for data models"""
import pytest
from datetime import datetime
from src.models import Calculation


class TestCalculationModel:
    """Test Calculation model"""
    
    def test_create_calculation_with_all_fields(self):
        """Test creating a Calculation with all fields"""
        calc = Calculation(
            process_name="Test Process",
            department="IT",
            people_involved=2,
            current_time_per_month=40,
            hourly_rate=100,
            complexity="Alta",
            systems_quantity=3,
            daily_transactions=1000,
            error_rate=2.5,
            exception_rate=1.5,
            expected_automation_percentage=80,
            rpa_implementation_cost=10000,
            maintenance_percentage=15,
            infra_license_cost=500,
            other_costs=1000,
            rpa_monthly_cost=500,
            fines_avoided=100,
            sql_savings=200,
            monthly_savings=5000,
            annual_savings=60000,
            payback_period_months=2,
            roi_first_year=50000,
            roi_percentage_first_year=500,
        )
        
        assert calc.process_name == "Test Process"
        assert calc.department == "IT"
        assert calc.people_involved == 2
        assert calc.complexity == "Alta"
        assert calc.systems_quantity == 3
        assert calc.monthly_savings == 5000
    
    def test_create_calculation_with_minimal_fields(self):
        """Test creating a Calculation with minimal required fields"""
        calc = Calculation(
            process_name="Simple Process",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        # Should have default values
        assert calc.department == ""  # Default
        assert calc.complexity == "Média"  # Default
        assert calc.systems_quantity == 1  # Default
        assert calc.daily_transactions == 100  # Default
        assert calc.error_rate == 0.0  # Default
        assert calc.exception_rate == 0.0  # Default
    
    def test_calculation_timestamps(self):
        """Test that timestamps are set automatically"""
        calc = Calculation(
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        assert calc.created_at is not None
        assert calc.updated_at is not None
        assert isinstance(calc.created_at, datetime)
        assert isinstance(calc.updated_at, datetime)
    
    def test_calculation_id_none_before_save(self):
        """Test that ID is None before saving to database"""
        calc = Calculation(
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        assert calc.id is None
    
    def test_calculation_with_zero_values(self):
        """Test calculation with zero values"""
        calc = Calculation(
            process_name="Zero Process",
            people_involved=1,
            current_time_per_month=0,
            hourly_rate=0,
            expected_automation_percentage=0,
            rpa_implementation_cost=0,
            rpa_monthly_cost=0,
            monthly_savings=0,
            annual_savings=0,
            payback_period_months=0,
            roi_first_year=0,
            roi_percentage_first_year=0,
        )
        
        assert calc.monthly_savings == 0
        assert calc.annual_savings == 0
        assert calc.payback_period_months == 0
    
    def test_calculation_with_negative_savings(self):
        """Test calculation with negative savings (loss scenario)"""
        calc = Calculation(
            process_name="Loss Process",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=0,  # No automation
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,  # High monthly cost, no automation
            monthly_savings=-500,  # Loss
            annual_savings=-6000,
            payback_period_months=float('inf'),
            roi_first_year=-16000,
            roi_percentage_first_year=-160,
        )
        
        assert calc.monthly_savings < 0
        assert calc.annual_savings < 0
        assert calc.payback_period_months == float('inf')
    
    def test_calculation_repr(self):
        """Test __repr__ method"""
        calc = Calculation(
            id=1,
            process_name="Test",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        repr_str = repr(calc)
        assert "Calculation" in repr_str
        assert "Test" in repr_str
        assert "140" in repr_str  # ROI percentage
    
    def test_calculation_different_complexities(self):
        """Test calculation with different complexity levels"""
        for complexity in ["Baixa", "Média", "Alta"]:
            calc = Calculation(
                process_name=f"Test {complexity}",
                complexity=complexity,
                people_involved=1,
                current_time_per_month=20,
                hourly_rate=50,
                expected_automation_percentage=50,
                rpa_implementation_cost=5000,
                rpa_monthly_cost=200,
                monthly_savings=1000,
                annual_savings=12000,
                payback_period_months=5,
                roi_first_year=7000,
                roi_percentage_first_year=140,
            )
            
            assert calc.complexity == complexity
    
    def test_calculation_with_large_numbers(self):
        """Test calculation with very large numbers"""
        calc = Calculation(
            process_name="Enterprise Process",
            people_involved=100,
            current_time_per_month=10000,
            hourly_rate=500,
            expected_automation_percentage=100,
            rpa_implementation_cost=1000000,
            rpa_monthly_cost=50000,
            monthly_savings=5000000,
            annual_savings=60000000,
            payback_period_months=0.2,
            roi_first_year=59000000,
            roi_percentage_first_year=5900,
        )
        
        assert calc.annual_savings == 60000000
        assert calc.roi_percentage_first_year == 5900
    
    def test_calculation_string_fields(self):
        """Test calculation with different string values"""
        calc = Calculation(
            process_name="Process with Special Chars: @#$%",
            department="Department-2024",
            people_involved=1,
            current_time_per_month=20,
            hourly_rate=50,
            expected_automation_percentage=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            monthly_savings=1000,
            annual_savings=12000,
            payback_period_months=5,
            roi_first_year=7000,
            roi_percentage_first_year=140,
        )
        
        assert calc.process_name == "Process with Special Chars: @#$%"
        assert calc.department == "Department-2024"
    
    def test_calculation_float_fields(self):
        """Test calculation with decimal float values"""
        calc = Calculation(
            process_name="Test",
            people_involved=1,
            current_time_per_month=20.5,
            hourly_rate=50.75,
            error_rate=2.345,
            exception_rate=1.234,
            expected_automation_percentage=50.5,
            rpa_implementation_cost=5000.99,
            maintenance_percentage=10.5,
            infra_license_cost=500.25,
            rpa_monthly_cost=200.50,
            monthly_savings=1000.75,
            annual_savings=12000.99,
            payback_period_months=5.5,
            roi_first_year=7000.50,
            roi_percentage_first_year=140.25,
        )
        
        assert calc.current_time_per_month == 20.5
        assert calc.hourly_rate == 50.75
        assert calc.error_rate == 2.345
