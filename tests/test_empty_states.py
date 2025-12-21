# -*- coding: utf-8 -*-
"""Tests for EmptyStateManager - UI empty states and components"""
import pytest
from io import StringIO
import sys
from unittest.mock import patch, MagicMock

from src.ui.empty_states import EmptyStateManager


class TestEmptyStateManager:
    """Test EmptyStateManager functionality"""
    
    def test_show_no_processes_empty_state_callable(self):
        """Test that show_no_processes_empty_state is callable"""
        assert callable(EmptyStateManager.show_no_processes_empty_state)
    
    def test_show_no_results_empty_state_callable(self):
        """Test that show_no_results_empty_state is callable"""
        assert callable(EmptyStateManager.show_no_results_empty_state)
    
    def test_show_no_reports_empty_state_callable(self):
        """Test that show_no_reports_empty_state is callable"""
        assert callable(EmptyStateManager.show_no_reports_empty_state)
    
    def test_show_deletion_confirmation_callable(self):
        """Test that show_deletion_confirmation is callable"""
        assert callable(EmptyStateManager.show_deletion_confirmation)
    
    def test_show_success_message_callable(self):
        """Test that show_success_message is callable"""
        assert callable(EmptyStateManager.show_success_message)
    
    def test_show_error_message_callable(self):
        """Test that show_error_message is callable"""
        assert callable(EmptyStateManager.show_error_message)
    
    def test_show_info_message_callable(self):
        """Test that show_info_message is callable"""
        assert callable(EmptyStateManager.show_info_message)
    
    def test_show_loading_with_spinner_callable(self):
        """Test that show_loading_with_spinner is callable"""
        assert callable(EmptyStateManager.show_loading_with_spinner)
    
    def test_show_metric_card_callable(self):
        """Test that show_metric_card is callable"""
        assert callable(EmptyStateManager.show_metric_card)
    
    def test_show_validation_error_callable(self):
        """Test that show_validation_error is callable"""
        assert callable(EmptyStateManager.show_validation_error)
    
    def test_show_validation_errors_callable(self):
        """Test that show_validation_errors is callable"""
        assert callable(EmptyStateManager.show_validation_errors)
    
    def test_show_feature_preview_callable(self):
        """Test that show_feature_preview is callable"""
        assert callable(EmptyStateManager.show_feature_preview)
    
    def test_create_responsive_layout_callable(self):
        """Test that create_responsive_layout is callable"""
        assert callable(EmptyStateManager.create_responsive_layout)
    
    def test_show_section_header_callable(self):
        """Test that show_section_header is callable"""
        assert callable(EmptyStateManager.show_section_header)
    
    def test_show_help_text_callable(self):
        """Test that show_help_text is callable"""
        assert callable(EmptyStateManager.show_help_text)
    
    def test_show_data_not_found_callable(self):
        """Test that show_data_not_found is callable"""
        assert callable(EmptyStateManager.show_data_not_found)


class TestEmptyStateMessages:
    """Test empty state message methods"""
    
    @patch('src.ui.empty_states.st')
    def test_show_success_message_with_default_icon(self, mock_st):
        """Test show_success_message with default icon"""
        EmptyStateManager.show_success_message("Test message")
        mock_st.success.assert_called_once_with("✅ Test message")
    
    @patch('src.ui.empty_states.st')
    def test_show_success_message_with_custom_icon(self, mock_st):
        """Test show_success_message with custom icon"""
        EmptyStateManager.show_success_message("Test message", icon="🎉")
        mock_st.success.assert_called_once_with("🎉 Test message")
    
    @patch('src.ui.empty_states.st')
    def test_show_error_message_with_default_icon(self, mock_st):
        """Test show_error_message with default icon"""
        EmptyStateManager.show_error_message("Error message")
        mock_st.error.assert_called_once_with("❌ Error message")
    
    @patch('src.ui.empty_states.st')
    def test_show_error_message_with_custom_icon(self, mock_st):
        """Test show_error_message with custom icon"""
        EmptyStateManager.show_error_message("Error message", icon="⚠️")
        mock_st.error.assert_called_once_with("⚠️ Error message")
    
    @patch('src.ui.empty_states.st')
    def test_show_info_message_with_default_icon(self, mock_st):
        """Test show_info_message with default icon"""
        EmptyStateManager.show_info_message("Info message")
        mock_st.info.assert_called_once_with("ℹ️ Info message")
    
    @patch('src.ui.empty_states.st')
    def test_show_info_message_with_custom_icon(self, mock_st):
        """Test show_info_message with custom icon"""
        EmptyStateManager.show_info_message("Info message", icon="📌")
        mock_st.info.assert_called_once_with("📌 Info message")


class TestValidationErrorDisplay:
    """Test validation error display methods"""
    
    @patch('src.ui.empty_states.st')
    def test_show_validation_error_single(self, mock_st):
        """Test showing single validation error"""
        EmptyStateManager.show_validation_error("Email", "Formato inválido")
        mock_st.error.assert_called_once()
    
    @patch('src.ui.empty_states.st')
    def test_show_validation_errors_empty_list(self, mock_st):
        """Test showing validation errors with empty list"""
        EmptyStateManager.show_validation_errors([])
        # Should not call anything for empty list
        assert not mock_st.subheader.called
    
    @patch('src.ui.empty_states.st')
    def test_show_validation_errors_multiple(self, mock_st):
        """Test showing multiple validation errors"""
        errors = ["Erro 1", "Erro 2", "Erro 3"]
        EmptyStateManager.show_validation_errors(errors)
        # Should call container and subheader
        assert mock_st.container.called


class TestLoadingSpinner:
    """Test loading spinner functionality"""
    
    @patch('src.ui.empty_states.st')
    def test_show_loading_with_spinner_returns_context(self, mock_st):
        """Test that show_loading_with_spinner returns a context manager"""
        mock_spinner = MagicMock()
        mock_st.spinner.return_value = mock_spinner
        
        result = EmptyStateManager.show_loading_with_spinner("Loading...")
        
        mock_st.spinner.assert_called_once_with("⏳ Loading...")
        assert result == mock_spinner
    
    @patch('src.ui.empty_states.st')
    def test_show_loading_with_spinner_custom_message(self, mock_st):
        """Test loading spinner with custom message"""
        mock_spinner = MagicMock()
        mock_st.spinner.return_value = mock_spinner
        
        EmptyStateManager.show_loading_with_spinner("Processando dados...")
        
        mock_st.spinner.assert_called_once_with("⏳ Processando dados...")


class TestMetricCard:
    """Test metric card display"""
    
    @patch('src.ui.empty_states.st')
    def test_show_metric_card_with_subtitle(self, mock_st):
        """Test showing metric card with subtitle"""
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        EmptyStateManager.show_metric_card("ROI", "250%", "Primeiro Ano")
        
        mock_st.columns.assert_called_once_with([0.5, 2, 0.5])
        mock_st.metric.assert_called_once_with("ROI", "250%")
        mock_st.caption.assert_called_once_with("Primeiro Ano")
    
    @patch('src.ui.empty_states.st')
    def test_show_metric_card_without_subtitle(self, mock_st):
        """Test showing metric card without subtitle"""
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        EmptyStateManager.show_metric_card("Economia", "R$ 50.000")
        
        mock_st.columns.assert_called_once_with([0.5, 2, 0.5])
        mock_st.metric.assert_called_once_with("Economia", "R$ 50.000")
        # caption should not be called when subtitle is None
        mock_st.caption.assert_not_called()


class TestHelpText:
    """Test help text display"""
    
    @patch('src.ui.empty_states.st')
    def test_show_help_text_with_default_title(self, mock_st):
        """Test help text with default title"""
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
        
        EmptyStateManager.show_help_text("Test help content")
        
        mock_st.expander.assert_called_once_with("💡 Dica")
    
    @patch('src.ui.empty_states.st')
    def test_show_help_text_with_custom_title(self, mock_st):
        """Test help text with custom title"""
        mock_st.expander.return_value.__enter__ = MagicMock()
        mock_st.expander.return_value.__exit__ = MagicMock(return_value=None)
        
        EmptyStateManager.show_help_text("Test help content", title="📖 Guia")
        
        mock_st.expander.assert_called_once_with("📖 Guia")


class TestSectionHeader:
    """Test section header display"""
    
    @patch('src.ui.empty_states.st')
    def test_show_section_header_with_icon(self, mock_st):
        """Test section header with icon"""
        EmptyStateManager.show_section_header("Test Section", icon="📊")
        
        # Should call markdown for header and divider
        assert mock_st.markdown.called
        mock_st.divider.assert_called_once()
    
    @patch('src.ui.empty_states.st')
    def test_show_section_header_without_icon(self, mock_st):
        """Test section header without icon"""
        EmptyStateManager.show_section_header("Test Section")
        
        # Should call markdown for header and divider
        assert mock_st.markdown.called
        mock_st.divider.assert_called_once()


class TestResponsiveLayout:
    """Test responsive layout creation"""
    
    @patch('src.ui.empty_states.st')
    def test_create_responsive_layout_default(self, mock_st):
        """Test creating responsive layout with default columns"""
        mock_st.columns.return_value = [MagicMock(), MagicMock(), MagicMock()]
        
        result = EmptyStateManager.create_responsive_layout()
        
        mock_st.columns.assert_called_once_with(3)
        assert len(result) == 3
    
    @patch('src.ui.empty_states.st')
    def test_create_responsive_layout_custom_columns(self, mock_st):
        """Test creating responsive layout with custom column count"""
        mock_st.columns.return_value = [MagicMock()] * 4
        
        result = EmptyStateManager.create_responsive_layout(num_columns=4)
        
        mock_st.columns.assert_called_once_with(4)
        assert len(result) == 4


class TestDataNotFound:
    """Test data not found empty state"""
    
    @patch('src.ui.empty_states.st')
    def test_show_data_not_found_default_type(self, mock_st):
        """Test data not found with default entity type"""
        EmptyStateManager.show_data_not_found()
        
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "Dados Não Encontrado" in call_args
    
    @patch('src.ui.empty_states.st')
    def test_show_data_not_found_custom_type(self, mock_st):
        """Test data not found with custom entity type"""
        EmptyStateManager.show_data_not_found(entity_type="Processos")
        
        mock_st.markdown.assert_called_once()
        call_args = mock_st.markdown.call_args[0][0]
        assert "Processos Não Encontrado" in call_args
