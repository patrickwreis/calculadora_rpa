# -*- coding: utf-8 -*-
"""Utility functions for calculations"""
from typing import List, Dict, Any, Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass


class InputValidator:
    """Validator for RPA ROI calculation inputs"""
    
    @staticmethod
    def validate_percentage(value: float, field_name: str, allow_zero: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate percentage values (0-100)
        
        Args:
            value: The percentage value to validate
            field_name: Name of the field for error messages
            allow_zero: Whether to allow zero value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        min_val = 0.0 if allow_zero else 0.01
        if not (min_val <= value <= 100.0):
            return False, f"{field_name} deve estar entre {min_val}% e 100%"
        return True, None
    
    @staticmethod
    def validate_positive_number(value: float, field_name: str, allow_zero: bool = True) -> Tuple[bool, Optional[str]]:
        """
        Validate positive numbers
        
        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            allow_zero: Whether to allow zero value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        min_val = 0.0 if allow_zero else 0.01
        if value < min_val:
            return False, f"{field_name} deve ser {'maior ou igual a 0' if allow_zero else 'maior que 0'}"
        return True, None
    
    @staticmethod
    def validate_integer_range(value: int, field_name: str, min_val: int, max_val: int) -> Tuple[bool, Optional[str]]:
        """
        Validate integer within range
        
        Args:
            value: The value to validate
            field_name: Name of the field for error messages
            min_val: Minimum allowed value
            max_val: Maximum allowed value
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not (min_val <= value <= max_val):
            return False, f"{field_name} deve estar entre {min_val} e {max_val}"
        return True, None
    
    @staticmethod
    def validate_cross_fields(
        error_rate: float,
        exception_rate: float,
        expected_automation_percentage: float
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate cross-field dependencies
        
        Args:
            error_rate: Error rate percentage
            exception_rate: Exception rate percentage
            expected_automation_percentage: Expected automation percentage
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Error rate + exception rate should not exceed 100%
        total_issues = error_rate + exception_rate
        if total_issues > 100.0:
            return False, f"Taxa de erro ({error_rate}%) + Taxa de exceção ({exception_rate}%) não pode exceder 100%"
        
        # Automação e exceção são conceitos independentes:
        # - Automação: % do processo feito por robô
        # - Exceção: % dos casos automatizados que precisam de revisão manual
        # Exemplo: 100% automatizado com 10% exceção = todos os 100 registros são processados
        # pelo robô, mas 10 deles precisam de validação humana após o processamento
        
        return True, None
    
    @classmethod
    def validate_all_inputs(cls, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate all input data comprehensively
        
        Args:
            data: Dictionary with all input fields
            
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        errors = []
        
        # Validate required fields exist
        required_fields = [
            'process_name', 'current_time_per_month', 'people_involved',
            'hourly_rate', 'rpa_implementation_cost', 'rpa_monthly_cost',
            'expected_automation_percentage'
        ]
        
        for field in required_fields:
            if field not in data or data[field] is None:
                errors.append(f"Campo obrigatório faltando: {field}")
        
        if errors:
            return False, errors
        
        # Validate process name
        if not isinstance(data['process_name'], str) or not data['process_name'].strip():
            errors.append("Nome do processo não pode estar vazio")
        
        # Validate positive numbers
        positive_fields = [
            ('current_time_per_month', 'Tempo atual por mês', False),
            ('hourly_rate', 'Taxa horária', False),
            ('rpa_implementation_cost', 'Custo de implementação', True),
            ('rpa_monthly_cost', 'Custo mensal RPA', True),
        ]
        
        for field, label, allow_zero in positive_fields:
            try:
                value = float(data[field])
                is_valid, error = cls.validate_positive_number(value, label, allow_zero)
                if not is_valid:
                    errors.append(error)
            except (ValueError, TypeError):
                errors.append(f"{label} deve ser um número válido")
        
        # Validate people_involved
        try:
            people = int(data['people_involved'])
            is_valid, error = cls.validate_integer_range(people, 'Pessoas envolvidas', 1, 10000)
            if not is_valid:
                errors.append(error)
        except (ValueError, TypeError):
            errors.append("Pessoas envolvidas deve ser um número inteiro válido")
        
        # Validate percentages
        percentage_fields = [
            ('expected_automation_percentage', 'Percentual de automação esperado'),
        ]
        
        for field, label in percentage_fields:
            try:
                value = float(data[field])
                is_valid, error = cls.validate_percentage(value, label, allow_zero=True)
                if not is_valid:
                    errors.append(error)
            except (ValueError, TypeError):
                errors.append(f"{label} deve ser um número válido")
        
        # Validate optional percentage fields
        optional_percentages = [
            ('error_rate', 'Taxa de erro'),
            ('exception_rate', 'Taxa de exceção'),
            ('maintenance_percentage', 'Percentual de manutenção'),
        ]
        
        for field, label in optional_percentages:
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    is_valid, error = cls.validate_percentage(value, label, allow_zero=True)
                    if not is_valid:
                        errors.append(error)
                except (ValueError, TypeError):
                    errors.append(f"{label} deve ser um número válido")
        
        # Validate cross-field dependencies
        if all(k in data for k in ['error_rate', 'exception_rate', 'expected_automation_percentage']):
            try:
                is_valid, error = cls.validate_cross_fields(
                    float(data.get('error_rate', 0)),
                    float(data.get('exception_rate', 0)),
                    float(data['expected_automation_percentage'])
                )
                if not is_valid:
                    errors.append(error)
            except (ValueError, TypeError):
                pass  # Already caught in individual validations
        
        # Validate additional benefits (if present)
        optional_positive = [
            ('fines_avoided', 'Multas evitadas'),
            ('sql_savings', 'SLA reduzida'),
        ]
        
        for field, label in optional_positive:
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    is_valid, error = cls.validate_positive_number(value, label, allow_zero=True)
                    if not is_valid:
                        errors.append(error)
                except (ValueError, TypeError):
                    errors.append(f"{label} deve ser um número válido")
        
        return len(errors) == 0, errors


def format_currency(value: float, currency: str = "BRL") -> str:
    """Format value as currency string"""
    if currency == "BRL":
        return f"R$ {value:,.2f}".replace(",", "_").replace(".", ",").replace("_", ".")
    return f"${value:,.2f}"


def format_percentage(value: float, decimals: int = 2) -> str:
    """Format value as percentage string"""
    return f"{value:.{decimals}f}%"


def format_months(months: float) -> str:
    """Format months as readable string"""
    if months == float('inf'):
        return "Indefinido"
    
    years = int(months // 12)
    remaining_months = int(months % 12)
    
    if years > 0 and remaining_months > 0:
        return f"{years}a {remaining_months}m"
    elif years > 0:
        return f"{years} ano{'s' if years > 1 else ''}"
    else:
        return f"{remaining_months} mês{'es' if remaining_months > 1 else ''}"


def validate_input(data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate calculation input data (legacy wrapper for compatibility)
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    is_valid, errors = InputValidator.validate_all_inputs(data)
    error_message = errors[0] if errors else ""
    return is_valid, error_message

def calculate_automation_metrics(
    expected_automation_percentage: float,
    exception_rate: float
) -> Dict[str, float]:
    """
    Calculate actual automation metrics based on expected automation and exception rate.
    
    Args:
        expected_automation_percentage: % of process that will be automated (0-100)
        exception_rate: % of automated tasks that need manual review (0-100)
    
    Returns:
        Dict with:
        - fully_automated_pct: % that runs 100% automatically (no intervention)
        - partial_review_pct: % that needs manual review despite automation
        - still_manual_pct: % that wasn't automated and remains manual
        - total_manual_effort_pct: Total % requiring manual work
    
    Example:
        80% expected automation, 20% exception rate:
        - fully_automated_pct = 80% × (1 - 20%) = 64%
        - partial_review_pct = 80% × 20% = 16%
        - still_manual_pct = 100% - 80% = 20%
        - total_manual_effort_pct = 16% + 20% = 36%
    """
    automation_ratio = expected_automation_percentage / 100.0
    exception_ratio = exception_rate / 100.0
    
    # Calculate each component
    fully_automated_pct = expected_automation_percentage * (1 - exception_ratio)
    partial_review_pct = expected_automation_percentage * exception_ratio
    still_manual_pct = 100.0 - expected_automation_percentage
    total_manual_effort_pct = partial_review_pct + still_manual_pct
    
    return {
        "fully_automated_pct": fully_automated_pct,
        "partial_review_pct": partial_review_pct,
        "still_manual_pct": still_manual_pct,
        "total_manual_effort_pct": total_manual_effort_pct,
    }