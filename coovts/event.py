"""The events a plugin has registered, and the subscriptions it sends for them."""

from collections.abc import Awaitable, Callable, Generator, Iterator
from functools import wraps
from typing import TYPE_CHECKING, Any, Protocol, cast, overload

from pydantic import BaseModel

from .errors import NetworkError
from .types import VTSBaseModel, get_event_config_model, get_event_name
from .types.api import EventSubscriptionRequest

if TYPE_CHECKING:
    from .types.api import EventSubscriptionResponse

type SubscriptionSender = Callable[
    [EventSubscriptionRequest],
    Awaitable["EventSubscriptionResponse"],
]


class DisposableCallable[**P, R](Protocol):
    """A handler `subscribe_event` wrapped: called exactly as it was, plus `dispose`."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R:
        """Called the way the handler itself is."""
        ...

    async def dispose(self) -> "EventSubscriptionResponse | None":
        """Give this handler's event up: cancel its subscription and forget it."""
        ...


class EventRegistration[T: BaseModel]:
    """One event: its model, its config and its handlers.

    Decorate with it to attach a handler, await it to subscribe now, or `dispose()` of it.
    """

    def __init__(
        self,
        registry: "EventSubscriptionRegistry",
        event_name: str,
        data_model: type[T] | None,
        config: Any,
    ) -> None:
        self._registry = registry
        self.event_name = event_name
        """The name VTube Studio pushes this event under."""
        self.data_model = data_model
        """The model frames are decoded into, or `None` when registered by name."""
        self.config = config
        """Whatever VTS accepts as this event's config, not necessarily a model."""
        self.handlers: list[Callable[[T], Any]] = []
        """The handlers attached to this event, in registration order."""

    def __call__[R](self, handler: Callable[[T], R]) -> DisposableCallable[[T], R]:
        """Attach a handler and hand it back wrapped, so it can give its own event up."""
        self.handlers.append(handler)

        @wraps(handler)
        def wrapper(data: T) -> R:
            return handler(data)

        wrapper.dispose = self.dispose  # type: ignore[attr-defined]
        return cast("DisposableCallable[[T], R]", wrapper)

    def __await__(self) -> Generator[Any, Any, "EventSubscriptionResponse"]:
        """Send this subscription now instead of at the next authentication."""
        return self._registry.send(self).__await__()

    async def dispose(self) -> "EventSubscriptionResponse | None":
        """Give this event up: cancel its subscription and forget it, handlers included."""
        return await self._registry.dispose(self)


class EventSubscriptionRegistry:
    """The events a plugin has registered, one `EventRegistration` per event name."""

    def __init__(self, send: SubscriptionSender) -> None:
        self._send = send
        self._registrations: dict[str, EventRegistration[Any]] = {}

    def get(self, event_name: str) -> EventRegistration[Any] | None:
        """The registration for an event name, as VTube Studio pushes it."""
        return self._registrations.get(event_name)

    def __iter__(self) -> Iterator[EventRegistration[Any]]:
        """Walk every registration; the walk runs over a snapshot."""
        return iter(tuple(self._registrations.values()))

    @overload
    def registration[T: BaseModel](
        self, data_model: type[T]
    ) -> EventRegistration[T]: ...
    @overload
    def registration(self, data_model: str) -> EventRegistration[Any]: ...
    def registration(
        self,
        data_model: type[BaseModel] | str,
    ) -> EventRegistration[Any]:
        """The registration for an event, created on first use; a name keeps it model-less."""
        event_name = (
            data_model if isinstance(data_model, str) else get_event_name(data_model)
        )
        registration = self._registrations.get(event_name)
        if registration is None:
            registration = EventRegistration(
                self,
                event_name,
                None if isinstance(data_model, str) else data_model,
                None,
            )
            self._registrations[event_name] = registration
        return registration

    @overload
    def subscribe[T: BaseModel](
        self,
        data_model: type[T],
        config: Any = None,
    ) -> EventRegistration[T]: ...
    @overload
    def subscribe(
        self,
        data_model: str,
        config: Any = None,
    ) -> EventRegistration[Any]: ...
    def subscribe(
        self,
        data_model: type[BaseModel] | str,
        config: Any = None,
    ) -> EventRegistration[Any]:
        """Register an event and the config it subscribes by; a model's config defaults when omitted.

        An event named by its wire name has no config model, so it gets an empty config instead; what
        VTS accepts there is VTS's business.
        """
        registration = self.registration(data_model)
        if config is not None:
            registration.config = config
        elif registration.data_model is None:
            registration.config = {}
        else:
            registration.config = default_event_config(registration.data_model)
        return registration

    async def dispose[T: BaseModel](
        self,
        registration: EventRegistration[T],
    ) -> "EventSubscriptionResponse | None":
        """Drop a registration, telling VTube Studio to stop pushing the event when it can."""
        if self._registrations.get(registration.event_name) is not registration:
            return None

        del self._registrations[registration.event_name]
        config = registration.config
        registration.config = None
        if config is None:
            return None

        try:
            return await self._send(
                _subscription_request(registration.event_name, config, subscribe=False),
            )
        except NetworkError:
            # Nothing is connected, so there is no live subscription left to cancel.
            return None

    async def send[T: BaseModel](
        self,
        registration: EventRegistration[T],
        *,
        subscribe: bool = True,
    ) -> "EventSubscriptionResponse":
        """Send one subscription frame for a live registration that carries a config."""
        if self._registrations.get(registration.event_name) is not registration:
            raise ValueError(
                f"The registration for {registration.event_name} is not live anymore",
            )
        config = registration.config
        if config is None:
            raise ValueError(
                f"The registration for {registration.event_name} carries no config, "
                "so there is nothing to subscribe with",
            )
        return await self._send(
            _subscription_request(registration.event_name, config, subscribe=subscribe),
        )


def _subscription_request(
    event_name: str,
    config: Any,
    *,
    subscribe: bool,
) -> EventSubscriptionRequest:
    """The frame that turns one event's subscription on or off."""
    return EventSubscriptionRequest(
        event_name=event_name,
        subscribe=subscribe,
        config=config,
    )


def default_event_config(data_model: type[BaseModel]) -> VTSBaseModel:
    """The config model of an event, built from its field defaults."""
    config_model = get_event_config_model(data_model)
    required = [
        name for name, field in config_model.model_fields.items() if field.is_required()
    ]
    if required:
        raise ValueError(
            f"{config_model.__name__} needs {', '.join(required)}; "
            f"pass config={config_model.__name__}(...) explicitly",
        )
    return config_model()
