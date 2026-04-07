"""
Enhanced AsyncObservable with key-specific subscriptions and on_change callback.

This module provides an extended Observable that adds:
- Key-specific subscriptions via subscribe_to_key()
- on_change callback for centralized side-effects
- Synchronous set() alongside async set_async()
- Version tracking for cache invalidation

Built on top of the base AsyncObservable from state/store.py.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from typing import TYPE_CHECKING, Any, Generic, TypeVar

if TYPE_CHECKING:
    pass

from .change_record import ChangeRecord

logger = logging.getLogger(__name__)

T = TypeVar("T")

Listener = Callable[[], None]
KeyListener = Callable[[ChangeRecord], None]
KeyListenerV = Callable[[ChangeRecord, int], None]
OnChange = Callable[[T, T], Awaitable[None] | None]


class AsyncObservable(Generic[T]):
    """
    Enhanced async-aware observable state store.

    Features:
    - Async-safe state mutations with locking
    - Key-specific subscriptions via subscribe_to_key()
    - Optional on_change callback for side-effects
    - Version tracking for cache invalidation
    - subscribe_to_key with ChangeRecord notifications

    This is an enhanced version of the base AsyncObservable in state/store.py.
    """

    def __init__(
        self,
        initial_state: T,
        *,
        on_change: OnChange[T] | None = None,
    ) -> None:
        self._state: T = initial_state
        self._listeners: list[Listener] = []
        self._key_listeners: dict[str, list[KeyListener]] = {}
        self._on_change: OnChange[T] | None = on_change
        self._lock = asyncio.Lock()
        self._version: int = 0

    def get(self) -> T:
        """Get current state synchronously (no copy - caller must not mutate)."""
        return self._state

    async def get_async(self) -> T:
        """Get current state asynchronously (with lock)."""
        async with self._lock:
            return self._state

    # Aliases for compatibility with base class
    def get_state_sync(self) -> T:
        """Alias for get() - synchronous state access."""
        return self._state

    async def get_state(self) -> T:
        """Alias for get_async() - async state access."""
        return await self.get_async()

    def set(self, updater: Callable[[T], T]) -> None:
        """
        Synchronous state update with equality check and notification.

        Uses identity check (not deep equality) to prevent infinite update loops.
        Calls on_change callbacks (fire-and-forget for async) before notifying listeners.

        Args:
            updater: Pure function that takes current state and returns new state.
        """
        new_state = updater(self._state)
        if new_state is self._state:
            return
        old_state = self._state
        saved_version = self._version
        self._state = new_state
        self._version += 1

        if self._on_change is not None:
            result = self._on_change(old_state, new_state)
            if asyncio.iscoroutine(result):
                if asyncio.get_running_loop():
                    asyncio.create_task(result)
                else:
                    loop = asyncio.new_event_loop()
                    loop.run_until_complete(result)
                    loop.close()

        self._notify_change(old_state, new_state, saved_version)

    async def set_async(
        self,
        updater: Callable[[T], T],
        *,
        await_effects: bool = True,
    ) -> None:
        """
        Async state update - optionally awaits on_change callback.

        Args:
            updater: Pure function that takes current state and returns new state.
            await_effects: If True, awaits on_change callback before notifying listeners.
        """
        new_state = updater(self._state)
        if new_state is self._state:
            return
        old_state = self._state
        saved_version = self._version
        self._state = new_state
        self._version += 1

        if self._on_change is not None and await_effects:
            result = self._on_change(old_state, new_state)
            if asyncio.iscoroutine(result):
                await result

        self._notify_change(old_state, new_state, saved_version)

    # Alias for compatibility
    async def set_state(self, new_state: T) -> None:
        """Set state directly (replaces old state). Alias for compatibility."""

        async def updater(_: T) -> T:
            return new_state

        await self.set_async(updater)

    def _notify_listeners(self, old_state: T, new_state: T) -> None:
        """Notify all listeners of state change."""
        for listener in self._listeners:
            try:
                listener()
            except Exception as e:
                logger.warning(f"AsyncObservable: listener error: {e}")

    def _notify_change(
        self,
        old_state: T,
        new_state: T,
        _saved_version: int | None = None,
    ) -> None:
        """Notify all listeners of state change."""
        # The version N for this change = saved_version (the version BEFORE increment).
        # We temporarily restore _version to N so that listeners reading store.version
        # see the right value, then restore to N+1 after.
        version_n = _saved_version if _saved_version is not None else self._version
        if _saved_version is not None:
            current_version = self._version
            self._version = _saved_version
        else:
            current_version = None

        try:
            self._notify_listeners(old_state, new_state)

            if isinstance(old_state, dict) and isinstance(new_state, dict):
                all_keys = set(old_state.keys()) | set(new_state.keys())
                for key in all_keys:
                    if old_state.get(key) != new_state.get(key):
                        record = ChangeRecord(
                            key=key,
                            old_value=old_state.get(key),
                            new_value=new_state.get(key),
                            timestamp=datetime.now(UTC),
                        )
                        for listener in self._key_listeners.get(key, []):
                            try:
                                listener(record, version_n)
                            except Exception as e:
                                logger.warning(
                                    f"AsyncObservable: key listener error: {e}"
                                )
        finally:
            if current_version is not None:
                self._version = current_version

    def subscribe(self, listener: Listener) -> Callable[[], None]:
        """
        Subscribe to any state change. Returns unsubscribe function.

        Args:
            listener: Callback called with no arguments on any state change.

        Returns:
            Unsubscribe function to remove the subscription.
        """
        self._listeners.append(listener)

        def unsubscribe() -> None:
            self._listeners.remove(listener)

        return unsubscribe

    async def subscribe_async(
        self, callback: Callable[[T, T], Awaitable[None]]
    ) -> Callable[[], None]:
        """
        Subscribe with async callback (new_state, old_state).

        Args:
            callback: Async function called with (new_state, old_state).

        Returns:
            Unsubscribe function.
        """
        self._listeners.append(callback)  # type: ignore

        def unsubscribe() -> None:
            self._listeners.remove(callback)  # type: ignore

        return unsubscribe

    def subscribe_sync(
        self, callback: Callable[[T, T], Awaitable[None]]
    ) -> Callable[[], None]:
        """
        Subscribe with async callback (for sync-compatible subscription).

        Alias for subscribe() - wraps the callback to ignore args.
        """
        async def wrapper() -> None:
            await callback(self._state, self._state)

        self._listeners.append(wrapper)

        def unsubscribe() -> None:
            self._listeners.remove(wrapper)

        return unsubscribe

    def subscribe_to_key(
        self,
        key: str,
        listener: KeyListener | KeyListenerV,
    ) -> Callable[[], None]:
        """
        Subscribe to changes for a specific key.

        Args:
            key: The state key to watch.
            listener: Called with a ChangeRecord and version number when the key changes.
                For backwards compatibility, if the listener only accepts one argument,
                it's wrapped to ignore the version.

        Returns:
            Unsubscribe function to remove the subscription.

        Example:
            unsub = store.subscribe_to_key("count", handle_count_change)

            def handle_count_change(record: ChangeRecord, version: int) -> None:
                print(f"count changed to {record.new_value} at version {version}")
        """
        import inspect

        # Wrap old-style listeners (1-arg) to accept the version param
        try:
            sig = inspect.signature(listener)
            num_params = sum(
                p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
                for p in sig.parameters.values()
            )
            if num_params == 1:
                old_listener: KeyListener = listener  # type: ignore
                wrapped: KeyListenerV = lambda record, _version, _l=old_listener: _l(record)
                listener = wrapped
        except (ValueError, TypeError):
            pass

        if key not in self._key_listeners:
            self._key_listeners[key] = []
        self._key_listeners[key].append(listener)

        def unsubscribe() -> None:
            if key in self._key_listeners:
                self._key_listeners[key].remove(listener)
                if not self._key_listeners[key]:
                    del self._key_listeners[key]

        return unsubscribe

    def unsubscribe(self, callback: Listener) -> None:
        """Remove a subscriber from the store."""
        self._listeners.remove(callback)

    @property
    def version(self) -> int:
        """Monotonically increasing version for cache invalidation."""
        return self._version

    def has_listeners(self) -> bool:
        """Return True if there are any active subscribers."""
        return len(self._listeners) > 0

    def listener_count(self) -> int:
        """Return the number of active subscribers."""
        return len(self._listeners)

    def __repr__(self) -> str:
        return (
            f"AsyncObservable(version={self._version}, "
            f"state_type={type(self._state).__name__}, "
            f"listeners={len(self._listeners)})"
        )
