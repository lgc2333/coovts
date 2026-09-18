# coovts

coovts is an async Python client for the VTube Studio plugin API: it owns one WebSocket
connection, the authentication handshake, the correlation of requests with their responses, and
the dispatch of inbound events to user code.

This file is the project's glossary — the words we use in code, issues and ADRs, and the words we
refuse to use for the same thing. It contains no implementation detail and no decisions; those
live in [`docs/adr/`](./docs/adr/).

## Language

### Runtime

**Plugin**:
The one object that owns a connection to VTube Studio and everything happening on it.
_Avoid_: Client, Connection, Session, Bot

**Hook**:
A lifecycle callback registered on a `Plugin` with a decorator (`@plugin.on_connected`), invoked at
a fixed moment of the connection lifecycle; several handlers per hook, in registration order.
_Avoid_: Callback, Listener, Signal, Event

**Handler**:
A function registered for one inbound event type; it runs as its own task and its result is never
awaited by the library.
_Avoid_: Callback, Subscriber, Listener

**Event subscription**:
The opt-in sent to VTube Studio that makes it push a given event. Distinct from a handler, which is
local: a subscription with no handler delivers frames nobody reads, and a handler without a
subscription never fires.
_Avoid_: Registration, Listen, Hook

**Request ID**:
The decimal-string identifier coovts assigns to an outbound API request so its response can be
matched to the code waiting for it. Owned by the library, never by user code.
_Avoid_: Correlation ID, UUID, Sequence number

**Pending request**:
An outbound API request that has been sent and whose response has not arrived. Pending requests do
not survive a disconnect: they fail with a network error, never being resumed, retried or re-sent.
_Avoid_: In-flight call, Awaiting future

**API timeout**:
The deadline, per request, after which a pending request is abandoned; an expired request raises
`RequestTimeout`. A timeout of `0` or `None` means "wait forever", not "fail immediately".
_Avoid_: Deadline, TTL

### Wire layer

**Envelope**:
The fields every frame carries regardless of payload (API name, API version, request ID, message
type), plus the payload itself.
_Avoid_: Header, Wrapper, Packet

**Message type**:
The wire string naming a frame's payload. It is always the class name of the API request model, so
renaming a model renames the protocol.
_Avoid_: API name, Command, Message name

**API request model**:
A model whose class name is the wire message type and which ends in `Request`.
_Avoid_: Payload, DTO, Command

**API response model**:
The model that decodes one request's answer. It is found from the request model — by a per-model
override if one exists, otherwise by swapping the `Request` suffix for `Response`.
_Avoid_: Result, Reply

**Event data model**:
The inbound model for one VTube Studio event. Its class name minus the `EventData` suffix is the
event name used for the subscription.
_Avoid_: Event payload, Message

**Event config model**:
The outbound model configuring an event subscription. Its class name minus the `EventConfig`
suffix matches the same event name as its event data model.
_Avoid_: Filter, Options

**Escape hatch**:
A class attribute (`msg_t`, `resp_t`, `resp_m`) overriding a name convention for a single model.
None is used today; they exist so an awkward name bends the convention instead of breaking it.
_Avoid_: Override, Exception

**Generated API surface**:
The typed signatures of `call_api` and `handle_event`, generated from the request and event models
into a stub file. Derived from the models, never edited by hand.
_Avoid_: Stub, Interface, Typing

### VTube Studio (upstream)

These are VTube Studio's words, not ours; they describe the application coovts talks to.

**VTube Studio (VTS)**:
The application coovts connects to over a local WebSocket; the source of the wire protocol and of
everything in this section.
_Avoid_: The app, the studio

**Model**:
A Live2D model loaded in VTS, and the thing most API calls operate on.
_Avoid_: Avatar, Character

**Live2D parameter**:
A named numeric input of a model. It must already exist before a plugin can inject into it, and a
parameter a plugin controls must be re-sent at least once per second.
_Avoid_: Variable, Slider, Input

**Hotkey**:
A model-defined trigger that a plugin can fire through the API.
_Avoid_: Shortcut, Button, Action

**Expression**:
A model-defined parameter preset that a plugin can activate.
_Avoid_: Animation, Pose

**Item**:
A prop loaded on top of a model, which can be moved, pinned and animated.
_Avoid_: Prop, Asset, Object

**Event**:
A push from VTS to the plugin (model loaded, hotkey triggered, model moved, …). Always the VTS
push, never a generic "something happened in Python".
_Avoid_: Callback, Notification, Signal, Message

**API error**:
A failed request reported by VTS itself, carrying an error ID and a message. Distinct from a
connection-level failure, which reaches a hook, and from a network error, which reaches whoever was
awaiting the request.
_Avoid_: Exception, Failure
