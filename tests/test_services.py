# -*- coding: utf-8 -*-
"""Tests for src/services modules"""
import pytest
import pandas as pd
from src.services import (
    MetricsCalculator,
    PageService,
    DataFrameBuilder,
    ChartFactory,
)
from src.models import Calculation
from src.calculator.utils import format_currency, format_months
from datetime import datetime


# ========== FIXTURES ==========
@pytest.fixture
def sample_calculation():
    """Create a sample calculation for testing"""
    return Calculation(
        id=1,
        user_id=1,
        process_name="Test Process",
        department="Finance",
        people_involved=2,
        current_time_per_month=160.0,
        hourly_rate=100.0,
        complexity="Média",
        systems_quantity=1,
        daily_transactions=100,
        error_rate=5.0,
        exception_rate=10.0,
        expected_automation_percentage=80.0,
        rpa_implementation_cost=20000.0,
        maintenance_percentage=10.0,
        infra_license_cost=500.0,
        other_costs=0.0,
        rpa_monthly_cost=500.0,
        fines_avoided=0.0,
        sql_savings=0.0,
        monthly_savings=11200.0,
        annual_savings=134400.0,
        payback_period_months=1.79,
        roi_first_year=134400.0,
        roi_percentage_first_year=672.0,
        classification="QUICK WIN",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def sample_calculations(sample_calculation):
    """Create multiple sample calculations"""
    calc1 = sample_calculation
    
    calc2 = Calculation(
        id=2,
        user_id=1,
        process_name="High ROI Process",
        department="Operations",
        people_involved=1,
        current_time_per_month=80.0,
        hourly_rate=100.0,
        complexity="Baixa",
        systems_quantity=1,
        daily_transactions=50,
        error_rate=2.0,
        exception_rate=5.0,
        expected_automation_percentage=95.0,
        rpa_implementation_cost=10000.0,
        maintenance_percentage=10.0,
        infra_license_cost=300.0,
        other_costs=0.0,
        rpa_monthly_cost=300.0,
        fines_avoided=0.0,
        sql_savings=0.0,
        monthly_savings=7200.0,
        annual_savings=86400.0,
        payback_period_months=0.12,
        roi_first_year=76400.0,
        roi_percentage_first_year=764.0,
        classification="QUICK WIN",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    calc3 = Calculation(
        id=3,
        user_id=1,
        process_name="Complex Process",
        department="IT",
        people_involved=3,
        current_time_per_month=200.0,
        hourly_rate=120.0,
        complexity="Alta",
        systems_quantity=5,
        daily_transactions=200,
        error_rate=15.0,
        exception_rate=20.0,
        expected_automation_percentage=25.0,
        rpa_implementation_cost=50000.0,
        maintenance_percentage=15.0,
        infra_license_cost=1000.0,
        other_costs=5000.0,
        rpa_monthly_cost=1000.0,
        fines_avoided=0.0,
        sql_savings=0.0,
        monthly_savings=1400.0,
        annual_savings=16800.0,
        payback_period_months=35.71,
        roi_first_year=-33200.0,
        roi_percentage_first_year=-66.4,
        classification="BAIXA PRIORIDADE",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    
    return [calc1, calc2, calc3]


# ========== METRICS CALCULATOR TESTS ==========
class TestMetricsCalculator:
    """Test MetricsCalculator service"""

    def test_aggregate_metrics_empty(self):
        """Test aggregation with empty list"""
        result = MetricsCalculator.aggregate_metrics([])
        assert result["total_processes"] == 0
        assert result["total_savings"] == 0.0
        assert result["avg_roi"] == 0.0
        assert result["avg_payback"] == 0.0

    def test_aggregate_metrics_single(self, sample_calculation):
        """Test aggregation with single calculation"""
        result = MetricsCalculator.aggregate_metrics([sample_calculation])
        assert result["total_processes"] == 1
        assert result["total_savings"] == sample_calculation.annual_savings
        assert result["avg_roi"] == sample_calculation.roi_percentage_first_year
        assert result["avg_payback"] == sample_calculation.payback_period_months

    def test_aggregate_metrics_multiple(self, sample_calculations):
        """Test aggregation with multiple calculations"""
        result = MetricsCalculator.aggregate_metrics(sample_calculations)
        assert result["total_processes"] == 3
        assert result["total_savings"] > 0
        assert result["total_investment"] > 0
        assert result["avg_roi"] > 0
        assert result["avg_payback"] > 0
        assert result["median_roi"] > 0
        assert result["median_payback"] > 0

    def test_classify_processes(self, sample_calculations):
        """Test process classification"""
        classification = MetricsCalculator.classify_processes(sample_calculations)
        
        assert "highly_automatable" in classification
        assert "partially_automatable" in classification
        assert "complex" in classification
        
        assert len(classification["highly_automatable"]) == 2  # 80% and 95%
        assert len(classification["partially_automatable"]) == 0
        assert len(classification["complex"]) == 1  # 25%

    def test_payback_distribution(self, sample_calculations):
        """Test payback distribution calculation"""
        dist = MetricsCalculator.payback_distribution(sample_calculations)
        
        assert "fast" in dist
        assert "medium" in dist
        assert "long" in dist
        
        assert dist["fast"]["count"] == 2  # < 6 months
        assert dist["medium"]["count"] == 0
        assert dist["long"]["count"] == 1  # > 12 months

    def test_roi_distribution(self, sample_calculations):
        """Test ROI distribution calculation"""
        dist = MetricsCalculator.roi_distribution(sample_calculations)
        
        assert "excellent" in dist
        assert "very_good" in dist
        assert "good" in dist
        assert "acceptable" in dist
        
        assert all(0 <= v["percentage"] <= 100 for v in dist.values())

    def test_top_by_metric_roi(self, sample_calculations):
        """Test top calculations by ROI"""
        top = MetricsCalculator.top_by_metric(sample_calculations, metric="roi", top=2)
        assert len(top) == 2
        assert top[0].roi_percentage_first_year >= top[1].roi_percentage_first_year

    def test_top_by_metric_payback(self, sample_calculations):
        """Test top calculations by payback (shortest first)"""
        top = MetricsCalculator.top_by_metric(sample_calculations, metric="payback", top=2)
        assert len(top) == 2
        assert top[0].payback_period_months <= top[1].payback_period_months

    def test_top_by_metric_savings(self, sample_calculations):
        """Test top calculations by savings"""
        top = MetricsCalculator.top_by_metric(sample_calculations, metric="savings", top=2)
        assert len(top) == 2
        assert top[0].annual_savings >= top[1].annual_savings

    def test_top_by_metric_count(self, sample_calculations):
        """Test top count parameter"""
        top1 = MetricsCalculator.top_by_metric(sample_calculations, top=1)
        top2 = MetricsCalculator.top_by_metric(sample_calculations, top=2)
        top5 = MetricsCalculator.top_by_metric(sample_calculations, top=5)
        
        assert len(top1) == 1
        assert len(top2) == 2
        assert len(top5) == 3  # Only 3 available


# ========== DATAFRAME BUILDER TESTS ==========
class TestDataFrameBuilder:
    """Test DataFrameBuilder service"""

    def test_build_calculations_table_empty(self):
        """Test DataFrame building with empty list"""
        df = DataFrameBuilder.build_calculations_table([])
        assert df.empty

    def test_build_calculations_table_single(self, sample_calculation):
        """Test DataFrame building with single calculation"""
        df = DataFrameBuilder.build_calculations_table([sample_calculation])
        
        assert len(df) == 1
        assert "Processo" in df.columns
        assert "Automação" in df.columns
        assert "ROI (%)" in df.columns

    def test_build_calculations_table_custom_columns(self, sample_calculation):
        """Test DataFrame building with custom columns"""
        df = DataFrameBuilder.build_calculations_table(
            [sample_calculation],
            columns=["process", "roi"]
        )
        
        assert "Processo" in df.columns
        assert "ROI (%)" in df.columns
        assert "Investimento" not in df.columns

    def test_build_calculations_table_with_rank(self, sample_calculations):
        """Test DataFrame building with rank column"""
        df = DataFrameBuilder.build_calculations_table(
            sample_calculations,
            columns=["rank", "process"],
            include_rank=True
        )
        
        assert "Posição" in df.columns
        assert len(df) == 3

    def test_build_metrics_comparison(self, sample_calculations):
        """Test metrics comparison table"""
        df = DataFrameBuilder.build_metrics_comparison(sample_calculations)
        
        assert "Posição" in df.columns
        assert "Processo" in df.columns
        assert len(df) == 3

    def test_build_detailed_table(self, sample_calculations):
        """Test detailed table building"""
        df = DataFrameBuilder.build_detailed_table(sample_calculations)
        
        assert "Processo" in df.columns
        assert "Economia/Ano" in df.columns
        assert "ROI (%)" in df.columns
        assert len(df) == 3

    def test_build_table_data_integrity(self, sample_calculation):
        """Test that data is correctly formatted in DataFrame"""
        df = DataFrameBuilder.build_calculations_table([sample_calculation])
        
        row = df.iloc[0]
        assert "R$" in row["Investimento"]  # Formatted currency
        assert "%" in row["Automação"]
        assert "%" in row["ROI (%)"]


# ========== CHART FACTORY TESTS ==========
class TestChartFactory:
    """Test ChartFactory service"""

    def test_bar_ranking_creation(self, sample_calculations):
        """Test bar ranking chart creation"""
        df = pd.DataFrame([
            {"Processo": c.process_name, "ROI (%)": c.roi_percentage_first_year}
            for c in sample_calculations
        ])
        
        fig = ChartFactory.bar_ranking(
            df,
            metric_col="ROI (%)",
            process_col="Processo",
            title="Test Chart"
        )
        
        assert fig is not None
        assert hasattr(fig, 'update_layout')

    def test_pie_distribution_creation(self):
        """Test pie distribution chart creation"""
        data = {
            "Category A": {"count": 10, "label": "Cat A"},
            "Category B": {"count": 20, "label": "Cat B"},
        }
        
        fig = ChartFactory.pie_distribution(data, title="Test Pie")
        
        assert fig is not None
        assert hasattr(fig, 'update_traces')

    def test_scatter_correlation_creation(self, sample_calculations):
        """Test scatter plot creation"""
        df = pd.DataFrame([
            {
                "ROI (%)": c.roi_percentage_first_year,
                "Payback (meses)": c.payback_period_months,
                "Economia/Ano": c.annual_savings,
            }
            for c in sample_calculations
        ])
        
        fig = ChartFactory.scatter_correlation(
            df,
            x_col="ROI (%)",
            y_col="Payback (meses)",
            size_col="Economia/Ano",
            title="Test Scatter"
        )
        
        assert fig is not None

    def test_histogram_distribution_creation(self, sample_calculations):
        """Test histogram creation"""
        df = pd.DataFrame([
            {"ROI (%)": c.roi_percentage_first_year}
            for c in sample_calculations
        ])
        
        fig = ChartFactory.histogram_distribution(
            df,
            col="ROI (%)",
            title="Test Histogram"
        )
        
        assert fig is not None

    def test_theme_colors(self):
        """Test theme color configuration"""
        themes = ChartFactory.THEME
        
        assert "roi" in themes
        assert "payback" in themes
        assert "savings" in themes
        assert "automation" in themes
        assert "default" in themes


# ========== PAGE SERVICE TESTS ==========
class TestPageService:
    """Test PageService utilities"""

    def test_get_user_context_structure(self, monkeypatch):
        """Test that get_user_context returns correct structure"""
        # Mock streamlit session_state
        mock_session = {
            "auth_user_id": 42,
            "auth_is_admin": True,
        }
        
        import streamlit as st
        monkeypatch.setattr(st, "session_state", mock_session)
        
        context = PageService.get_user_context()
        
        assert "current_user_id" in context
        assert "is_admin" in context
        assert "user_filter" in context
        assert context["current_user_id"] == 42
        assert context["is_admin"] is True

    def test_user_filter_for_admin(self, monkeypatch):
        """Test that admins get None filter (see all)"""
        mock_session = {
            "auth_user_id": 1,
            "auth_is_admin": True,
        }
        
        import streamlit as st
        monkeypatch.setattr(st, "session_state", mock_session)
        
        context = PageService.get_user_context()
        assert context["user_filter"] is None  # Admin sees all

    def test_user_filter_for_regular_user(self, monkeypatch):
        """Test that regular users get their ID as filter"""
        mock_session = {
            "auth_user_id": 5,
            "auth_is_admin": False,
        }
        
        import streamlit as st
        monkeypatch.setattr(st, "session_state", mock_session)
        
        context = PageService.get_user_context()
        assert context["user_filter"] == 5  # User sees only their data


# ========== INTEGRATION TESTS ==========
class TestServicesIntegration:
    """Integration tests for services working together"""

    def test_metrics_to_dataframe_workflow(self, sample_calculations):
        """Test workflow: metrics -> dataframe -> chart"""
        # Get metrics
        metrics = MetricsCalculator.aggregate_metrics(sample_calculations)
        assert metrics["total_processes"] == 3
        
        # Get top processes
        top = MetricsCalculator.top_by_metric(sample_calculations, top=2)
        
        # Build DataFrame
        df = DataFrameBuilder.build_calculations_table(top)
        assert len(df) == 2
        
        # Create chart
        fig = ChartFactory.bar_ranking(
            df,
            metric_col="ROI (%)",
            process_col="Processo"
        )
        assert fig is not None

    def test_classification_workflow(self, sample_calculations):
        """Test workflow: classify -> build tables for each category"""
        classification = MetricsCalculator.classify_processes(sample_calculations)
        
        # Build table for highly automatable
        df_high = DataFrameBuilder.build_calculations_table(
            classification["highly_automatable"]
        )
        assert len(df_high) == 2
        
        # Build table for complex
        df_complex = DataFrameBuilder.build_calculations_table(
            classification["complex"]
        )
        assert len(df_complex) == 1
