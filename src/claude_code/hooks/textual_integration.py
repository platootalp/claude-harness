"""
Textual Integration - Component state subscription for Textual apps.

Provides integration between the AppStateStore and Textual components,
enabling reactive state binding and lifecycle management.

Migrated from src/hooks/useTextualBinding.ts pattern.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .app_state_store import AppStateStore
    from .change_record import ChangeRecord


@dataclass
class StateSubscription:
    """
    Manages a component's subscription to the app state store.

    Automatically subscribes on mount and unsubscribes on cleanup.
    Supports both global change subscriptions and key-specific subscriptions.

    Example:
        class MyWidget(Static):
            def __init__(self):
                super().__init__()
                self._sub: StateSubscription | None = None

            def on_mount(self) -> None:
                self._sub = StateSubscription(
                    store=get_app_state(),
                    on_change=self._render,
                    keys=["count", "name"],
                )
                self._sub.attach()

            def _render(self) -> None:
                state = self._sub.store.get()
                self.update(f"Count: {state.get('count', 0)}")

            def on_unmount(self) -> None:
                if self._sub:
                    self._sub.detach()
    """

    store: "AppStateStore"
    on_change: Callable[[], None]
    keys: list[str] = field(default_factory=list)
    _unsubs: list[Callable[[], None]] = field(default_factory=list, repr=False)
    _first_render: bool = field(default=True, init=False)

    def attach(self) -> None:
        """
        Subscribe to the store.

        Does NOT call on_change() here - the first store change will trigger
        the initial render (capturing the correct version), and subsequent
        changes will also call on_change().

        Should be called in the component's on_mount handler.
        """
        if self.keys:
            # Key-specific subscriptions
            for key in self.keys:
                unsub = self.store.subscribe_to_key(
                    key,
                    lambda record, ver, key=key: self._handle_key_change(record, ver),
                )
                self._unsubs.append(unsub)
        else:
            # Global subscription - wrap to capture version at notification time
            def wrapped_listener() -> None:
                # Read store.version while version is still at the correct value
                # (before _notify_change restores it after notification)
                _ = self.store.version
                self.on_change()

            unsub = self.store.subscribe(wrapped_listener)
            self._unsubs.append(unsub)

    def _handle_key_change(
        self, record: "ChangeRecord", version: int
    ) -> None:
        """Handle a key-specific change record."""
        if self._first_render:
            self._first_render = False
        self.on_change()

    def detach(self) -> None:
        """
        Unsubscribe from all state changes.

        Should be called in the component's on_unmount handler.
        """
        for unsub in self._unsubs:
            try:
                unsub()
            except Exception:
                pass
        self._unsubs.clear()

    def update_keys(self, new_keys: list[str]) -> None:
        """
        Update the list of keys to watch.

        Re-subscribes to the new key set.

        Args:
            new_keys: New list of keys to subscribe to.
        """
        self.detach()
        self.keys = new_keys
        self.attach()


class SelectorSubscription:
    """
    Subscription that uses a selector for efficient updates.

    Only notifies when the selected value changes, not on every state change.
    More efficient than StateSubscription for components that only care
    about specific state slices.

    Example:
        class TaskList(Static):
            def __init__(self):
                super().__init__()
                self._sub: SelectorSubscription | None = None

            def on_mount(self) -> None:
                from .selector import SelectorState

                selector = SelectorState(
                    get_app_state(),
                    selector=lambda s: s.get("tasks", {})
                )
                self._sub = SelectorSubscription(
                    selector=selector,
                    on_change=self._render,
                )
                self._sub.attach()

            def _render(self) -> None:
                tasks = self._sub.get_value()
                self.update(f"Tasks: {len(tasks)}")

            def on_unmount(self) -> None:
                if self._sub:
                    self._sub.detach()
    """

    def __init__(
        self,
        selector: Any,  # SelectorState
        on_change: Callable[[], None],
    ) -> None:
        self._selector = selector
        self._on_change = on_change
        self._unsub: Callable[[], None] | None = None

    def attach(self) -> None:
        """Start listening for selector changes."""
        self._unsub = self._selector.subscribe(self._on_change)
        self._on_change()

    def detach(self) -> None:
        """Stop listening."""
        if self._unsub is not None:
            self._unsub()
            self._unsub = None

    def get_value(self) -> Any:
        """Get the current selected value."""
        return self._selector.get()


def create_widget_subscription(
    store: "AppStateStore",
    keys: list[str],
    render: Callable[[], None],
) -> StateSubscription:
    """
    Factory function to create a StateSubscription for a Textual widget.

    Convenience wrapper that creates and attaches a subscription in one call.

    Args:
        store: The AppStateStore to subscribe to.
        keys: List of state keys to watch.
        render: Function called to re-render the widget.

    Returns:
        A StateSubscription ready for use. Call detach() in on_unmount.

    Example:
        class MyWidget(Static):
            def __init__(self):
                super().__init__()
                self._sub = create_widget_subscription(
                    get_app_state(),
                    keys=["notifications"],
                    render=self.refresh,
                )

            def on_mount(self) -> None:
                self._sub.attach()

            def refresh(self) -> None:
                self.update(str(get_app_state().get().get("notifications")))

            def on_unmount(self) -> None:
                self._sub.detach()
    """
    sub = StateSubscription(store=store, on_change=render, keys=keys)
    return sub
