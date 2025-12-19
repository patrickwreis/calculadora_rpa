# -*- coding: utf-8 -*-
"""Utility functions for calculations"""
from typing import List, Dict, Any


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


def validate_input(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate calculation input data
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    required_fields = [
        'process_name', 'current_time_per_month', 'people_involved',
        'hourly_rate', 'rpa_implementation_cost', 'rpa_monthly_cost',
        'expected_automation_percentage'
    ]
    
    for field in required_fields:
        if field not in data or data[field] is None:
            return False, f"Campo obrigatório faltando: {field}"
    
    # Validate numeric fields
    numeric_validations = {
        'current_time_per_month': (0, float('inf')),
        'people_involved': (1, 10000),
        'hourly_rate': (0, float('inf')),
        'rpa_implementation_cost': (0, float('inf')),
        'rpa_monthly_cost': (0, float('inf')),
        'expected_automation_percentage': (0, 100),
    }
    
    for field, (min_val, max_val) in numeric_validations.items():
        try:
            value = float(data[field])
            if not (min_val <= value <= max_val):
                return False, f"{field} deve estar entre {min_val} e {max_val}"
        except (ValueError, TypeError):
            return False, f"{field} deve ser um número"
    
    return True, ""
