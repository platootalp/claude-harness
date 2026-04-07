"""
Tests for hooks/textual_integration.py - Textual component state subscriptions.
"""

from __future__ import annotations

import pytest

from src.claude_code.hooks.app_state_store import AppStateStore
from src.claude_code.hooks.selector import SelectorState
from src.claude_code.hooks.textual_integration import (
    SelectorSubscription,
    StateSubscription,
    create_widget_subscription,
)


class TestStateSubscription:
    """Tests for StateSubscription."""

    def test_attach_subscribes_and_renders(self) -> None:
        """attach() subscribes and calls on_change."""
        store = AppStateStore()
        render_calls: list[int] = []

        sub = StateSubscription(store, lambda: render_calls.append(store.version))
        sub.attach()
        assert render_calls == [0]  # initial render

        sub.detach()

    def test_key_subscription(self) -> None:
        """Key-specific subscriptions only fire for those keys."""
        store = AppStateStore({"count": 0, "name": "a"})
        render_calls: list[int] = []

        sub = StateSubscription(
            store, lambda: render_calls.append(store.version), keys=["count"]
        )
        sub.attach()

        store.set(lambda s: {**s, "name": "b"})  # count unchanged
        assert render_calls == [0]  # only initial

        store.set(lambda s: {**s, "count": 5})
        assert render_calls == [0, 1]  # new render for count change

        sub.detach()

    def test_detach_unsubscribes(self) -> None:
        """detach() stops all subscriptions."""
        store = AppStateStore({"x": 0})
        calls: list = []

        sub = StateSubscription(store, lambda: calls.append(1), keys=["x"])
        sub.attach()
        sub.detach()

        store.set(lambda s: {**s, "x": 99})
        assert len(calls) == 0

    def test_update_keys_resubscribes(self) -> None:
        """update_keys() resubscribes to new key set."""
        store = AppStateStore({"a": 0, "b": 0})
        calls: list[int] = []

        sub = StateSubscription(store, lambda: calls.append(store.version), keys=["a"])
        sub.attach()
        assert calls == [0]

        store.set(lambda s: {**s, "a": 1})
        assert calls == [0, 1]

        sub.update_keys(["b"])
        # re-attach calls on_change
        store.set(lambda s: {**s, "b": 1})
        assert calls == [0, 1, 2]  # new version after re-attach


class TestSelectorSubscription:
    """Tests for SelectorSubscription."""

    def test_attach_and_get_value(self) -> None:
        """SelectorSubscription attaches and returns value."""
        store = AppStateStore({"items": [1, 2, 3]})
        selector = SelectorState(store, lambda s: len(s.get("items", [])))
        calls: list[int] = []

        sub = SelectorSubscription(selector, lambda: calls.append(selector.get()))
        sub.attach()
        assert sub.get_value() == 3
        assert calls == [3]

        sub.detach()

    def test_only_fires_on_selected_change(self) -> None:
        """SelectorSubscription only fires when selected value changes."""
        store = AppStateStore({"items": [1, 2, 3], "other": "foo"})
        selector = SelectorState(store, lambda s: len(s.get("items", [])))
        calls: list = []

        sub = SelectorSubscription(selector, lambda: calls.append(1))
        sub.attach()

        store.set(lambda s: {**s, "other": "bar"})  # items unchanged
        assert len(calls) == 0

        store.set(lambda s: {**s, "items": [1]})  # items changed
        assert len(calls) == 1

        sub.detach()


class TestCreateWidgetSubscription:
    """Tests for create_widget_subscription factory."""

    def test_creates_and_attachs_subscription(self) -> None:
        """Factory creates a ready-to-use subscription."""
        store = AppStateStore()
        calls: list = []

        sub = create_widget_subscription(store, ["x"], lambda: calls.append(1))
        sub.attach()
        assert calls == [1]

        sub.detach()
