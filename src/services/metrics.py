"""Metrics calculation and aggregation service"""
from typing import List, Dict, Optional
from src.models import Calculation


class MetricsCalculator:
    """Centralized metrics aggregation and classification"""

    @staticmethod
    def aggregate_metrics(calculations: List[Calculation]) -> Dict[str, float]:
        """Calculate all aggregated metrics at once
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Dictionary with aggregated metrics
        """
        if not calculations:
            return {
                "total_processes": 0,
                "total_savings": 0.0,
                "total_investment": 0.0,
                "avg_roi": 0.0,
                "avg_payback": 0.0,
                "median_roi": 0.0,
                "median_payback": 0.0,
                "min_payback": 0.0,
                "max_payback": 0.0,
                "min_roi": 0.0,
                "max_roi": 0.0,
            }

        roi_list = [c.roi_percentage_first_year for c in calculations]
        payback_list = [c.payback_period_months for c in calculations]
        
        sorted_roi = sorted(roi_list)
        sorted_payback = sorted(payback_list)
        
        n = len(calculations)
        median_roi = sorted_roi[n // 2] if n > 0 else 0.0
        median_payback = sorted_payback[n // 2] if n > 0 else 0.0

        return {
            "total_processes": len(calculations),
            "total_savings": sum(c.annual_savings for c in calculations),
            "total_investment": sum(c.rpa_implementation_cost for c in calculations),
            "avg_roi": sum(roi_list) / len(calculations),
            "avg_payback": sum(payback_list) / len(calculations),
            "median_roi": median_roi,
            "median_payback": median_payback,
            "min_payback": min(payback_list),
            "max_payback": max(payback_list),
            "min_roi": min(roi_list),
            "max_roi": max(roi_list),
        }

    @staticmethod
    def classify_processes(calculations: List[Calculation]) -> Dict[str, List[Calculation]]:
        """Classify processes by automation potential
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Dict with three lists: highly_automatable, partially_automatable, complex
        """
        return {
            "highly_automatable": [
                c for c in calculations
                if c.expected_automation_percentage >= 70
            ],
            "partially_automatable": [
                c for c in calculations
                if 30 <= c.expected_automation_percentage < 70
            ],
            "complex": [
                c for c in calculations
                if c.expected_automation_percentage < 30
            ],
        }

    @staticmethod
    def payback_distribution(calculations: List[Calculation]) -> Dict[str, Dict]:
        """Get payback period distribution
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Dict with counts and percentages by payback category
        """
        fast = [c for c in calculations if c.payback_period_months < 6]
        medium = [c for c in calculations if 6 <= c.payback_period_months <= 12]
        long = [c for c in calculations if c.payback_period_months > 12]
        
        total = len(calculations)
        
        return {
            "fast": {
                "count": len(fast),
                "percentage": (len(fast) / total * 100) if total > 0 else 0,
                "label": "Rápido (< 6 meses)"
            },
            "medium": {
                "count": len(medium),
                "percentage": (len(medium) / total * 100) if total > 0 else 0,
                "label": "Médio (6-12 meses)"
            },
            "long": {
                "count": len(long),
                "percentage": (len(long) / total * 100) if total > 0 else 0,
                "label": "Longo (> 12 meses)"
            },
        }

    @staticmethod
    def roi_distribution(calculations: List[Calculation]) -> Dict[str, Dict]:
        """Get ROI distribution
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Dict with counts and percentages by ROI category
        """
        excellent = [c for c in calculations if c.roi_percentage_first_year >= 500]
        very_good = [c for c in calculations if 200 <= c.roi_percentage_first_year < 500]
        good = [c for c in calculations if 50 <= c.roi_percentage_first_year < 200]
        acceptable = [c for c in calculations if c.roi_percentage_first_year < 50]
        
        total = len(calculations)
        
        return {
            "excellent": {
                "count": len(excellent),
                "percentage": (len(excellent) / total * 100) if total > 0 else 0,
                "label": "Excelente (≥ 500%)"
            },
            "very_good": {
                "count": len(very_good),
                "percentage": (len(very_good) / total * 100) if total > 0 else 0,
                "label": "Muito Bom (200-500%)"
            },
            "good": {
                "count": len(good),
                "percentage": (len(good) / total * 100) if total > 0 else 0,
                "label": "Bom (50-200%)"
            },
            "acceptable": {
                "count": len(acceptable),
                "percentage": (len(acceptable) / total * 100) if total > 0 else 0,
                "label": "Aceitável (< 50%)"
            },
        }

    @staticmethod
    def top_by_metric(
        calculations: List[Calculation],
        metric: str = "roi",
        top: int = 10
    ) -> List[Calculation]:
        """Get top N processes by specified metric
        
        Args:
            calculations: List of Calculation objects
            metric: One of 'roi', 'payback', 'savings', 'investment'
            top: Number of top items to return
            
        Returns:
            Sorted list of calculations
        """
        if metric == "roi":
            key = lambda c: c.roi_percentage_first_year
            reverse = True
        elif metric == "payback":
            key = lambda c: c.payback_period_months
            reverse = False
        elif metric == "savings":
            key = lambda c: c.annual_savings
            reverse = True
        elif metric == "investment":
            key = lambda c: c.rpa_implementation_cost
            reverse = True
        else:
            key = lambda c: c.roi_percentage_first_year
            reverse = True
        
        return sorted(calculations, key=key, reverse=reverse)[:top]
