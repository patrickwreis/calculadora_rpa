"""DataFrame builder for consistent data transformations"""
from typing import List, Optional
import pandas as pd
from src.models import Calculation
from src.ui.components import format_currency, format_months


class DataFrameBuilder:
    """Unified DataFrame creation for calculations"""

    @staticmethod
    def build_calculations_table(
        calculations: List[Calculation],
        columns: Optional[List[str]] = None,
        include_rank: bool = False
    ) -> pd.DataFrame:
        """Build standardized calculations table
        
        Args:
            calculations: List of Calculation objects
            columns: Specific columns to include (None = all)
            include_rank: Add ranking column
            
        Returns:
            Formatted DataFrame
        """
        if not calculations:
            return pd.DataFrame()

        all_columns = {
            "rank": "Posição",
            "process": "Processo",
            "department": "Departamento",
            "automation": "Automação",
            "investment": "Investimento",
            "monthly_savings": "Economia/Mês",
            "annual_savings": "Economia/Ano",
            "roi": "ROI (%)",
            "payback": "Payback (meses)",
            "automation_capacity": "Capacidade (h/mês)",
        }

        if columns is None:
            columns = ["process", "automation", "investment", "annual_savings", "roi", "payback"]

        data = []
        for i, calc in enumerate(calculations, 1):
            row = {
                "rank": i,
                "process": calc.process_name,
                "department": getattr(calc, 'department', 'N/A') or 'N/A',
                "automation": f"{calc.expected_automation_percentage:.0f}%",
                "investment": format_currency(calc.rpa_implementation_cost),
                "monthly_savings": format_currency(calc.monthly_savings),
                "annual_savings": format_currency(calc.annual_savings),
                "roi": f"{calc.roi_percentage_first_year:.1f}%",
                "payback": format_months(calc.payback_period_months),
                "automation_capacity": f"{calc.automation_capacity:.0f}h",
            }

            # Filter to requested columns
            filtered_row = {}
            if include_rank and "rank" in columns:
                filtered_row["Posição"] = row["rank"]
            
            for col_key in columns:
                if col_key in row and col_key in all_columns:
                    filtered_row[all_columns[col_key]] = row[col_key]

            data.append(filtered_row)

        return pd.DataFrame(data)

    @staticmethod
    def build_metrics_comparison(
        calculations: List[Calculation]
    ) -> pd.DataFrame:
        """Build comparison table for top processes
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Comparison DataFrame
        """
        return DataFrameBuilder.build_calculations_table(
            calculations,
            columns=["rank", "process", "automation", "annual_savings", "roi", "payback"],
            include_rank=True
        )

    @staticmethod
    def build_detailed_table(
        calculations: List[Calculation]
    ) -> pd.DataFrame:
        """Build detailed table with all metrics
        
        Args:
            calculations: List of Calculation objects
            
        Returns:
            Detailed DataFrame
        """
        return DataFrameBuilder.build_calculations_table(
            calculations,
            columns=["process", "department", "automation", "investment", 
                    "monthly_savings", "annual_savings", "roi", "payback", 
                    "automation_capacity"]
        )
