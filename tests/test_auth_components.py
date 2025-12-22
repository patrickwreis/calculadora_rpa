# -*- coding: utf-8 -*-
"""Unit tests for auth_components helpers (UI-safe with mocked Streamlit)."""
from unittest.mock import patch

import pytest

import src.ui.auth_components as ac


class TestValidationHelpers:
    @pytest.mark.parametrize(
        "email,expected",
        [
            ("user@example.com", (True, None)),
            ("", (False, "Email é obrigatório")),
            ("bad-email", (False, "Formato de email inválido")),
            ("a" * 255 + "@example.com", (False, "Email muito longo")),
        ],
    )
    def test_validate_email(self, email, expected):
        assert ac.validate_email(email) == expected

    @pytest.mark.parametrize(
        "password,expected_valid",
        [
            ("abc123", True),
            ("abcdef", False),  # missing digit
            ("123456", False),  # missing letter
            ("", False),
            ("a" * 129, False),
        ],
    )
    def test_validate_password(self, password, expected_valid):
        ok, _ = ac.validate_password(password)
        assert ok is expected_valid

    @pytest.mark.parametrize(
        "password,expected_label",
        [
            ("abc123", "Fraca"),  # short and low complexity
            ("Abc123!!", "Forte"),
            ("abc", "Fraca"),
        ],
    )
    def test_get_password_strength(self, password, expected_label):
        label, _ = ac.get_password_strength(password)
        assert label == expected_label

    def test_sanitize_input_trims_and_strips_control_chars(self):
        dirty = "  hello\x01world\n"
        assert ac.sanitize_input(dirty) == "helloworld"


class TestUiRendering:
    def test_show_password_strength_renders_when_password_present(self):
        with patch("streamlit.markdown") as mock_md:
            ac.show_password_strength("abc123!!")
            assert mock_md.called

    def test_show_password_strength_skips_when_empty(self):
        with patch("streamlit.markdown") as mock_md:
            ac.show_password_strength("")
            mock_md.assert_not_called()

    def test_show_auth_success_message(self):
        with patch("streamlit.success") as mock_success, patch("streamlit.balloons") as mock_balloons:
            ac.show_auth_success_message("user@example.com")
            mock_success.assert_called_once()
            mock_balloons.assert_called_once()

    def test_show_register_success_message(self):
        with patch("streamlit.success") as mock_success, patch("streamlit.info") as mock_info:
            ac.show_register_success_message()
            mock_success.assert_called_once()
            mock_info.assert_called_once()
