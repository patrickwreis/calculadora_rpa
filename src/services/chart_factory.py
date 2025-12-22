"""Chart factory for consistent visualizations"""
from typing import Optional
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go


class ChartFactory:
    """Factory for creating standardized charts"""

    # Theme colors
    THEME = {
        "roi": "RdYlGn",
        "payback": "Blues",
        "savings": "Greens",
        "automation": "Viridis",
        "default": "Blues",
    }

    @staticmethod
    def bar_ranking(
        data: pd.DataFrame,
        metric_col: str,
        process_col: str = "Processo",
        title: str = "",
        ascending: bool = False,
        theme: Optional[str] = None,
        height: int = 500
    ) -> go.Figure:
        """Create ranking bar chart
        
        Args:
            data: DataFrame with data
            metric_col: Column name for values
            process_col: Column name for labels
            title: Chart title
            ascending: Sort ascending (default False = descending)
            theme: Color theme (default auto-detect)
            height: Chart height in pixels
            
        Returns:
            Plotly figure
        """
        if theme is None:
            theme = ChartFactory.THEME.get(metric_col.lower(), ChartFactory.THEME["default"])

        # Sort data
        sorted_data = data.sort_values(metric_col, ascending=ascending)

        fig = px.bar(
            sorted_data,
            x=metric_col,
            y=process_col,
            orientation='h',
            color=metric_col,
            color_continuous_scale=theme,
            title=title,
            height=height,
            labels={metric_col: metric_col, process_col: process_col}
        )

        fig.update_layout(
            margin=dict(l=200, r=20, t=40, b=20),
            hovermode="closest",
            showlegend=False,
        )

        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='LightGray')

        return fig

    @staticmethod
    def pie_distribution(
        data: dict,
        title: str = "",
        height: int = 400
    ) -> go.Figure:
        """Create pie chart for distribution
        
        Args:
            data: Dict with labels and counts
            title: Chart title
            height: Chart height in pixels
            
        Returns:
            Plotly figure
        """
        labels = [v.get("label", k) for k, v in data.items()]
        values = [v.get("count", 0) for v in data.values()]
        
        fig = px.pie(
            values=values,
            names=labels,
            title=title,
            height=height,
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        
        return fig

    @staticmethod
    def scatter_correlation(
        data: pd.DataFrame,
        x_col: str,
        y_col: str,
        size_col: Optional[str] = None,
        color_col: Optional[str] = None,
        title: str = "",
        height: int = 500
    ) -> go.Figure:
        """Create scatter plot for correlation analysis
        
        Args:
            data: DataFrame with data
            x_col: X-axis column
            y_col: Y-axis column
            size_col: Optional size column
            color_col: Optional color column
            title: Chart title
            height: Chart height in pixels
            
        Returns:
            Plotly figure
        """
        fig = px.scatter(
            data,
            x=x_col,
            y=y_col,
            size=size_col,
            color=color_col,
            title=title,
            height=height,
            hover_data=data.columns,
        )

        fig.update_layout(
            hovermode="closest",
            showlegend=True,
        )

        return fig

    @staticmethod
    def histogram_distribution(
        data: pd.DataFrame,
        col: str,
        title: str = "",
        nbins: int = 20,
        height: int = 400
    ) -> go.Figure:
        """Create histogram for distribution analysis
        
        Args:
            data: DataFrame with data
            col: Column to analyze
            title: Chart title
            nbins: Number of bins
            height: Chart height in pixels
            
        Returns:
            Plotly figure
        """
        fig = px.histogram(
            data,
            x=col,
            nbins=nbins,
            title=title,
            height=height,
            color_discrete_sequence=["#1f77b4"],
        )

        fig.update_layout(
            hovermode="closest",
            showlegend=False,
        )

        return fig
