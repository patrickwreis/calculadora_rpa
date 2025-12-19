# -*- coding: utf-8 -*-
"""Extended tests for ROI Calculator"""
import pytest
from src.calculator.roi_calculator import ROICalculator, ROIInput, ROIResult


class TestROICalculatorBasic:
    """Test basic ROI calculation"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_calculate_basic(self, calculator):
        """Test basic ROI calculation"""
        input_data = ROIInput(
            process_name="Test Process",
            current_time_per_month=40,  # hours
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result = calculator.calculate(input_data)
        
        assert isinstance(result, ROIResult)
        assert result.monthly_savings > 0
        assert result.annual_savings > 0
        assert result.roi_percentage_first_year > 0
    
    def test_calculate_returns_correct_type(self, calculator):
        """Test that calculate returns ROIResult"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=20,
            people_involved=1,
            hourly_rate=50,
            rpa_implementation_cost=5000,
            rpa_monthly_cost=200,
            expected_automation_percentage=50,
        )
        
        result = calculator.calculate(input_data)
        
        assert hasattr(result, 'monthly_savings')
        assert hasattr(result, 'annual_savings')
        assert hasattr(result, 'payback_period_months')
        assert hasattr(result, 'roi_first_year')
        assert hasattr(result, 'roi_percentage_first_year')
        assert hasattr(result, 'automation_capacity')


class TestROICalculatorSavings:
    """Test savings calculations"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_monthly_savings_calculation(self, calculator):
        """Test monthly savings is calculated correctly"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,  # 100 hours
            people_involved=1,
            hourly_rate=100,  # $100/hour
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,  # $500/month for RPA
            expected_automation_percentage=100,  # 100% automated
        )
        
        result = calculator.calculate(input_data)
        
        # Current cost: 100 * 100 = $10,000/month
        # Automated cost: 0 (100% automated)
        # Monthly savings: $10,000 - $0 - $500 (RPA cost) = $9,500
        assert result.monthly_savings == 9500
    
    def test_partial_automation(self, calculator):
        """Test partial automation scenario"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=50,  # 50% automated
        )
        
        result = calculator.calculate(input_data)
        
        # Current cost: 100 * 100 = $10,000/month
        # Automated cost: $10,000 * 0.5 = $5,000/month
        # Monthly savings: $10,000 - $5,000 - $500 = $4,500
        assert result.monthly_savings == 4500
    
    def test_zero_automation(self, calculator):
        """Test scenario with no automation"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=0,
        )
        
        result = calculator.calculate(input_data)
        
        # Current cost: 100 * 100 = $10,000/month
        # Automated cost: $10,000 * 1.0 = $10,000/month (no automation)
        # Monthly savings: $10,000 - $10,000 - $500 = -$500 (negative!)
        assert result.monthly_savings < 0
    
    def test_annual_savings(self, calculator):
        """Test annual savings calculation"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result = calculator.calculate(input_data)
        
        # Monthly savings: 100 * 100 * 0.8 - 500 = 8000 - 500 = 7500
        # Annual savings: 7500 * 12 = 90000
        assert result.annual_savings == result.monthly_savings * 12


class TestROICalculatorPayback:
    """Test payback period calculations"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_payback_period_calculation(self, calculator):
        """Test payback period is calculated correctly"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=100,
        )
        
        result = calculator.calculate(input_data)
        
        # Monthly savings: 100 * 100 - 500 = 9500
        # Payback: 10000 / 9500 = 1.05 months
        assert 1 < result.payback_period_months < 2
    
    def test_payback_period_infinity_no_savings(self, calculator):
        """Test payback period is infinity when there are no savings"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=0,
        )
        
        result = calculator.calculate(input_data)
        
        # No savings, so payback should be infinity
        assert result.payback_period_months == float('inf')


class TestROICalculatorMultiplePeople:
    """Test calculations with multiple people"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_multiple_people_increases_savings(self, calculator):
        """Test that more people means more savings"""
        input_data_1_person = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        input_data_5_people = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=5,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result_1 = calculator.calculate(input_data_1_person)
        result_5 = calculator.calculate(input_data_5_people)
        
        # More people = more total hours = more savings
        assert result_5.monthly_savings > result_1.monthly_savings
        assert result_5.annual_savings > result_1.annual_savings


class TestROICalculatorRateVariations:
    """Test calculations with different hourly rates"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_higher_hourly_rate_increases_savings(self, calculator):
        """Test that higher hourly rates increase savings"""
        input_data_low_rate = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=50,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        input_data_high_rate = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=200,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result_low = calculator.calculate(input_data_low_rate)
        result_high = calculator.calculate(input_data_high_rate)
        
        assert result_high.monthly_savings > result_low.monthly_savings


class TestROICalculatorEdgeCases:
    """Test edge cases and boundary conditions"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_zero_implementation_cost(self, calculator):
        """Test scenario with no implementation cost"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=0,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result = calculator.calculate(input_data)
        
        # Payback should be immediate (0 or very small)
        assert result.payback_period_months <= 0.01
    
    def test_very_high_monthly_cost(self, calculator):
        """Test scenario with very high RPA monthly cost"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=1,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=9500,  # Almost all the savings
            expected_automation_percentage=100,
        )
        
        result = calculator.calculate(input_data)
        
        # Should have minimal savings
        assert result.monthly_savings < 1000
    
    def test_automation_capacity(self, calculator):
        """Test automation capacity calculation"""
        input_data = ROIInput(
            process_name="Test",
            current_time_per_month=100,
            people_involved=2,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        result = calculator.calculate(input_data)
        
        # Automation capacity should be calculated
        assert result.automation_capacity > 0


class TestROICalculatorMultiple:
    """Test calculating multiple processes"""
    
    @pytest.fixture
    def calculator(self):
        return ROICalculator()
    
    def test_calculate_multiple(self, calculator):
        """Test calculating multiple processes at once"""
        inputs = [
            ROIInput(
                process_name="Process 1",
                current_time_per_month=40,
                people_involved=1,
                hourly_rate=100,
                rpa_implementation_cost=10000,
                rpa_monthly_cost=500,
                expected_automation_percentage=80,
            ),
            ROIInput(
                process_name="Process 2",
                current_time_per_month=20,
                people_involved=2,
                hourly_rate=50,
                rpa_implementation_cost=5000,
                rpa_monthly_cost=200,
                expected_automation_percentage=50,
            ),
            ROIInput(
                process_name="Process 3",
                current_time_per_month=100,
                people_involved=3,
                hourly_rate=75,
                rpa_implementation_cost=15000,
                rpa_monthly_cost=1000,
                expected_automation_percentage=90,
            ),
        ]
        
        results = calculator.calculate_multiple(inputs)
        
        assert len(results) == 3
        assert all(isinstance(r, ROIResult) for r in results)
        assert all(r.annual_savings > 0 for r in results)
    
    def test_calculate_multiple_empty(self, calculator):
        """Test calculating with empty list"""
        results = calculator.calculate_multiple([])
        assert results == []
    
    def test_calculate_multiple_single(self, calculator):
        """Test calculating with single process"""
        inputs = [
            ROIInput(
                process_name="Single Process",
                current_time_per_month=40,
                people_involved=1,
                hourly_rate=100,
                rpa_implementation_cost=10000,
                rpa_monthly_cost=500,
                expected_automation_percentage=80,
            ),
        ]
        
        results = calculator.calculate_multiple(inputs)
        
        assert len(results) == 1
        assert results[0].monthly_savings > 0



    """Test ROIInput dataclass"""
    
    def test_roi_input_creation(self):
        """Test creating ROIInput"""
        input_data = ROIInput(
            process_name="Test Process",
            current_time_per_month=40,
            people_involved=2,
            hourly_rate=100,
            rpa_implementation_cost=10000,
            rpa_monthly_cost=500,
            expected_automation_percentage=80,
        )
        
        assert input_data.process_name == "Test Process"
        assert input_data.current_time_per_month == 40
        assert input_data.people_involved == 2
        assert input_data.hourly_rate == 100
        assert input_data.rpa_implementation_cost == 10000
        assert input_data.rpa_monthly_cost == 500
        assert input_data.expected_automation_percentage == 80


class TestROIResult:
    """Test ROIResult dataclass"""
    
    def test_roi_result_creation(self):
        """Test creating ROIResult"""
        result = ROIResult(
            monthly_savings=5000,
            annual_savings=60000,
            payback_period_months=2,
            roi_first_year=50000,
            roi_percentage_first_year=500,
            automation_capacity=100,
        )
        
        assert result.monthly_savings == 5000
        assert result.annual_savings == 60000
        assert result.payback_period_months == 2
        assert result.roi_first_year == 50000
        assert result.roi_percentage_first_year == 500
        assert result.automation_capacity == 100
