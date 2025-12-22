# -*- coding: utf-8 -*-
"""Tests for production-used EmptyStateManager methods."""
from unittest.mock import patch, MagicMock

from src.ui.empty_states import EmptyStateManager


def test_show_no_processes_empty_state_renders_layout_and_button():
    """Render should show layout and button without navigating by default."""
    with patch("streamlit.markdown") as mock_md, \
         patch("streamlit.columns") as mock_cols, \
         patch("streamlit.button") as mock_btn, \
         patch("streamlit.switch_page") as mock_switch:

        mock_cols.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_btn.return_value = False

        EmptyStateManager.show_no_processes_empty_state()

        assert mock_md.called
        assert mock_cols.called
        assert mock_btn.called
        mock_switch.assert_not_called()


def test_show_no_processes_empty_state_triggers_navigation_when_clicked():
    """Clicking the CTA should navigate to the new process page."""
    with patch("streamlit.markdown"), \
         patch("streamlit.columns") as mock_cols, \
         patch("streamlit.button") as mock_btn, \
         patch("streamlit.switch_page") as mock_switch:

        mock_cols.return_value = (MagicMock(), MagicMock(), MagicMock())
        mock_btn.return_value = True

        EmptyStateManager.show_no_processes_empty_state()

        mock_switch.assert_called_once_with("pages/2_Novo_processo.py")


def test_show_error_message_uses_default_icon():
    """Default error icon should prefix the message."""
    with patch("streamlit.error") as mock_err:
        EmptyStateManager.show_error_message("Falha ao carregar")
        mock_err.assert_called_once_with("❌ Falha ao carregar")


def test_show_error_message_allows_custom_icon():
    """Should allow overriding the icon when provided."""
    with patch("streamlit.error") as mock_err:
        EmptyStateManager.show_error_message("Falha ao carregar", icon="⚠️")
        mock_err.assert_called_once_with("⚠️ Falha ao carregar")

