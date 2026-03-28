"""
Tests for the OAuth CLI helpers.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import AsyncMock, patch

import pytest

from ticktick_sdk.auth_cli import run_auth_flow, run_manual_mode


pytestmark = [pytest.mark.unit, pytest.mark.errors]


class TestAuthCLI:
    """Tests for the OAuth CLI flow."""

    async def test_run_auth_flow_uses_callback_state(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """The token exchange should use the callback-provided state."""
        monkeypatch.setenv("TICKTICK_CLIENT_ID", "test-client-id")
        monkeypatch.setenv("TICKTICK_CLIENT_SECRET", "test-client-secret")

        fake_token = SimpleNamespace(
            access_token="test-access-token",
            expires_in=None,
            refresh_token=None,
        )

        with patch("ticktick_sdk.auth_cli.OAuth2Handler") as MockHandler:
            handler = MockHandler.return_value
            handler.get_authorization_url.return_value = ("https://ticktick.com/oauth/authorize", "generated-state")
            handler.exchange_code = AsyncMock(return_value=fake_token)

            with patch(
                "ticktick_sdk.auth_cli.run_manual_mode",
                new=AsyncMock(return_value=("auth-code", "callback-state")),
            ):
                exit_code = await run_auth_flow(manual=True)

        assert exit_code == 0
        handler.exchange_code.assert_awaited_once_with(code="auth-code", state="callback-state")

    async def test_run_manual_mode_parses_callback_url(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Manual mode should extract both code and state from callback data."""
        monkeypatch.setattr(
            "builtins.input",
            lambda _: "http://127.0.0.1:8080/callback?code=test-code&state=test-state",
        )

        code, state = await run_manual_mode(handler=None, auth_url="https://ticktick.com/oauth/authorize")  # type: ignore[arg-type]

        assert code == "test-code"
        assert state == "test-state"
