# -*- coding: utf-8 -*-
"""Integration Tests - Full workflow testing"""
import pytest
from src.database.db_manager import DatabaseManager
from src.calculator import ROICalculator, ROIInput
from src.calculator.utils import InputValidator


class TestFullCalculationWorkflow:
    """Test complete calculation workflow from input to database save"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance"""
        return DatabaseManager()
    
    @pytest.fixture
    def calculator(self):
        """Create a ROICalculator instance"""
        return ROICalculator()
    
    def test_complete_calculation_workflow(self, db_manager, calculator):
        """Test complete workflow: validate input -> calculate -> save to DB"""
        # Step 1: Validate input
        input_data = {
            'process_name': 'Integration Test Process',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'error_rate': 5.0,
            'exception_rate': 10.0,
            'fines_avoided': 500.0,
            'sql_savings': 300.0,
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(input_data)
        assert is_valid is True
        assert len(errors) == 0
        
        # Step 2: Create ROI input and calculate
        roi_input = ROIInput(
            process_name=input_data['process_name'],
            current_time_per_month=input_data['current_time_per_month'],
            people_involved=int(input_data['people_involved']),
            hourly_rate=input_data['hourly_rate'],
            rpa_implementation_cost=input_data['rpa_implementation_cost'],
            rpa_monthly_cost=input_data['rpa_monthly_cost'],
            expected_automation_percentage=input_data['expected_automation_percentage'],
        )
        
        result = calculator.calculate(roi_input)
        assert result is not None
        assert result.monthly_savings > 0
        
        # Step 3: Calculate extended metrics
        extended_metrics = calculator.calculate_extended_roi(
            base_result=result,
            implementation_cost=input_data['rpa_implementation_cost'],
            fines_avoided=input_data['fines_avoided'],
            sql_savings=input_data['sql_savings']
        )
        
        assert extended_metrics['total_monthly_savings'] > result.monthly_savings
        assert extended_metrics['roi_1year_percentage'] > 0
        
        # Step 4: Save to database
        calculation_data = {
            'process_name': input_data['process_name'],
            'department': 'IT',
            'people_involved': int(input_data['people_involved']),
            'current_time_per_month': input_data['current_time_per_month'],
            'hourly_rate': input_data['hourly_rate'],
            'complexity': 'Média',
            'systems_quantity': 2,
            'daily_transactions': 500,
            'error_rate': input_data['error_rate'],
            'exception_rate': input_data['exception_rate'],
            'expected_automation_percentage': input_data['expected_automation_percentage'],
            'rpa_implementation_cost': input_data['rpa_implementation_cost'],
            'maintenance_percentage': 10.0,
            'infra_license_cost': 500.0,
            'other_costs': 1000.0,
            'rpa_monthly_cost': input_data['rpa_monthly_cost'],
            'fines_avoided': input_data['fines_avoided'],
            'sql_savings': input_data['sql_savings'],
            'monthly_savings': extended_metrics['total_monthly_savings'],
            'annual_savings': extended_metrics['total_annual_savings'],
            'payback_period_months': extended_metrics['payback_period_months'],
            'roi_first_year': extended_metrics['economia_1year'],
            'roi_percentage_first_year': extended_metrics['roi_1year_percentage'],
        }
        
        success, saved_calc, error_msg = db_manager.save_calculation(calculation_data)
        assert success is True
        assert saved_calc is not None
        assert saved_calc.id is not None
        assert saved_calc.process_name == 'Integration Test Process'
        
        # Step 5: Retrieve from database
        success, retrieved_calc, error_msg = db_manager.get_calculation(saved_calc.id)
        assert success is True
        assert retrieved_calc is not None
        assert retrieved_calc.id == saved_calc.id
        assert retrieved_calc.monthly_savings == extended_metrics['total_monthly_savings']


class TestCRUDWorkflow:
    """Test Create, Read, Update, Delete workflow"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance"""
        return DatabaseManager()
    
    @pytest.fixture
    def sample_data(self):
        """Sample calculation data"""
        return {
            'process_name': 'CRUD Test Process',
            'department': 'Finance',
            'people_involved': 3,
            'current_time_per_month': 200.0,
            'hourly_rate': 75.0,
            'complexity': 'Baixa',
            'systems_quantity': 1,
            'daily_transactions': 1000,
            'error_rate': 2.0,
            'exception_rate': 5.0,
            'expected_automation_percentage': 90.0,
            'rpa_implementation_cost': 8000.0,
            'maintenance_percentage': 10.0,
            'infra_license_cost': 300.0,
            'other_costs': 500.0,
            'rpa_monthly_cost': 150.0,
            'fines_avoided': 200.0,
            'sql_savings': 100.0,
            'monthly_savings': 2500.0,
            'annual_savings': 30000.0,
            'payback_period_months': 3.2,
            'roi_first_year': 22000.0,
            'roi_percentage_first_year': 275.0,
        }
    
    def test_create_read_update_delete(self, db_manager, sample_data):
        """Test complete CRUD workflow"""
        # CREATE
        success_create, created_calc, error_msg = db_manager.save_calculation(sample_data)
        assert success_create is True
        assert created_calc is not None
        calc_id = created_calc.id
        
        # READ
        success_read, read_calc, error_msg = db_manager.get_calculation(calc_id)
        assert success_read is True
        assert read_calc is not None
        assert read_calc.process_name == 'CRUD Test Process'
        
        # UPDATE
        updated_data = {'process_name': 'CRUD Test Updated', 'monthly_savings': 3000.0}
        success_update, updated_calc, error_msg = db_manager.update_calculation(calc_id, updated_data)
        assert success_update is True
        assert updated_calc is not None
        assert updated_calc.process_name == 'CRUD Test Updated'
        assert updated_calc.monthly_savings == 3000.0
        
        # Verify UPDATE worked
        success_verify, verified_calc, _ = db_manager.get_calculation(calc_id)
        assert verified_calc.process_name == 'CRUD Test Updated'
        
        # DELETE
        success_delete, error_msg = db_manager.delete_calculation(calc_id)
        assert success_delete is True
        
        # Verify DELETE worked
        success_check, deleted_calc, _ = db_manager.get_calculation(calc_id)
        assert deleted_calc is None


class TestMultipleCalculationsWorkflow:
    """Test workflow with multiple calculations"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance"""
        return DatabaseManager()
    
    @pytest.fixture
    def calculator(self):
        """Create a ROICalculator instance"""
        return ROICalculator()
    
    def test_create_and_retrieve_multiple_calculations(self, db_manager, calculator):
        """Test creating and retrieving multiple calculations"""
        # Create 3 different calculations
        calc_ids = []
        
        for i in range(3):
            input_data = {
                'process_name': f'Process {i+1}',
                'current_time_per_month': 100.0 + (i * 20),
                'people_involved': i + 1,
                'hourly_rate': 50.0,
                'rpa_implementation_cost': 5000.0,
                'rpa_monthly_cost': 200.0,
                'expected_automation_percentage': 70.0 + (i * 5),
            }
            
            roi_input = ROIInput(**input_data)
            result = calculator.calculate(roi_input)
            
            calc_data = {
                'process_name': input_data['process_name'],
                'department': f'Dept {i+1}',
                'people_involved': int(input_data['people_involved']),
                'current_time_per_month': input_data['current_time_per_month'],
                'hourly_rate': input_data['hourly_rate'],
                'complexity': 'Média',
                'systems_quantity': i + 1,
                'daily_transactions': 500,
                'error_rate': 5.0,
                'exception_rate': 5.0,
                'expected_automation_percentage': input_data['expected_automation_percentage'],
                'rpa_implementation_cost': input_data['rpa_implementation_cost'],
                'maintenance_percentage': 10.0,
                'infra_license_cost': 500.0,
                'other_costs': 1000.0,
                'rpa_monthly_cost': input_data['rpa_monthly_cost'],
                'fines_avoided': 0.0,
                'sql_savings': 0.0,
                'monthly_savings': result.monthly_savings,
                'annual_savings': result.annual_savings,
                'payback_period_months': result.payback_period_months,
                'roi_first_year': result.roi_first_year,
                'roi_percentage_first_year': result.roi_percentage_first_year,
            }
            
            success, saved_calc, _ = db_manager.save_calculation(calc_data)
            assert success is True
            calc_ids.append(saved_calc.id)
        
        # Retrieve all calculations
        success_all, all_calcs, _ = db_manager.get_all_calculations()
        assert success_all is True
        assert len(all_calcs) >= 3
        
        # Verify each calculation
        for calc_id in calc_ids:
            success, calc, _ = db_manager.get_calculation(calc_id)
            assert success is True
            assert calc is not None
        
        # Clean up
        for calc_id in calc_ids:
            db_manager.delete_calculation(calc_id)


class TestErrorRecoveryWorkflow:
    """Test error handling and recovery in workflows"""
    
    @pytest.fixture
    def db_manager(self):
        """Create a DatabaseManager instance"""
        return DatabaseManager()
    
    def test_invalid_input_handling(self):
        """Test handling of invalid input"""
        # Invalid: automation > 100%
        invalid_data = {
            'process_name': 'Invalid Process',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 150.0,  # Invalid!
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(invalid_data)
        assert is_valid is False
        assert len(errors) > 0
    
    def test_invalid_cross_field_validation(self):
        """Test cross-field validation errors"""
        # Invalid: error_rate + exception_rate > 100%
        invalid_data = {
            'process_name': 'Cross Field Invalid',
            'current_time_per_month': 160.0,
            'people_involved': 2,
            'hourly_rate': 50.0,
            'rpa_implementation_cost': 5000.0,
            'rpa_monthly_cost': 200.0,
            'expected_automation_percentage': 80.0,
            'error_rate': 60.0,
            'exception_rate': 50.0,  # 60 + 50 = 110% > 100%
        }
        
        is_valid, errors = InputValidator.validate_all_inputs(invalid_data)
        assert is_valid is False
        assert any("100%" in str(e) for e in errors)
    
    def test_database_operation_error_handling(self, db_manager):
        """Test error handling in database operations"""
        # Try to get non-existent calculation
        success, calc, error_msg = db_manager.get_calculation(99999)
        assert success is True  # Operation succeeded (idempotent)
        assert calc is None  # But no calculation found
        
        # Try to update non-existent calculation
        success, calc, error_msg = db_manager.update_calculation(99999, {'process_name': 'Test'})
        assert success is True  # Operation succeeded (idempotent)
        assert calc is None  # But no calculation updated
        
        # Try to delete non-existent calculation
        success, error_msg = db_manager.delete_calculation(99999)
        assert success is True  # Operation succeeded (idempotent - no error for non-existent)
