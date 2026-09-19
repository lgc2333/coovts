---
status: accepted
amends: ['0009']
---

# Events are declared, and the library keeps them subscribed

A VTS event needs two things that live in different places: a subscription, which is what makes VTS
push the event and which dies with the session, and a handler, which is local and survives a
reconnect. The library used to own only the second one: `handle_event` registered a handler, and the
subscription was a hand-built `EventSubscriptionRequest` sent from `on_authenticated` — the one place
where a forgotten line silently produces a handler that never fires, and where the config was typed
`Any`.

`plugin.subscribe_event(data_model, config=None)` now returns an `EventRegistration`: the record of
one event, holding its data model, the config its subscription carries, and its handlers. It is the
declaration of both halves at once. Decorating with it attaches a handler, so `handle_event` keeps
working for a handler without a subscription; awaiting it sends the subscription immediately and
hands back `EventSubscriptionResponse`, which is what a dynamic config needs.

Every declaration is re-sent after each successful authentication, before `on_authenticated` is
dispatched, so a reconnect cannot lose a subscription and user code can rely on it being live. A
subscription VTS refuses reaches `on_subscribe_failed` with the registration and the error instead of
failing the session — a declaration is re-sent on every authentication, so a refusal has to be
survivable; one that was awaited instead raises at the await, where a caller can act on it. A refusal
would otherwise repeat on every reconnect and, for an event that only exists on the beta branch, never
succeed. Decorating attaches a handler and hands it back
wrapped, so the function a caller decorated carries `dispose()` of its own event:
`await on_moved.dispose()` cancels the subscription when a session is up and forgets the
registration, handlers included. There is no `unsubscribe_event` on the plugin, because the thing a
caller declared with is the thing it gives up, and a declaration nobody kept a reference to is one
nobody can cancel.

The pairing runs on the name convention that already names events: a data model resolves to its
config model through `get_event_config_model`, and a declaration with no config is built from that
model's field defaults. A config that has a required field cannot be defaulted, so the generated stub
requires it for exactly those events — the requirement comes from the model's own fields rather than
from a hand-kept list.

The registry of declarations is a module of its own (`coovts/event.py`) rather than more
state inside `Plugin`, the same way request correlation lives in `coovts/request.py`: the plugin
drives it, but the bookkeeping is not part of the connection.

`handle_event(data_model)` is the same registration with no config, and it hands back the same wrapped
handler, so a handler that was never subscribed to can still be disposed of. It needs no generated
overload — a generic method on `Plugin` types it — and naming an event by its wire name is what covers
what this package does not model: no data model, so no decoding, no validation and no
`on_parse_data_error`, handlers that get the raw payload, and a subscription that carries an empty
config unless one is given. Decoding is decided per handler, so naming an event that something else
modelled leaves those handlers decoded and the named ones raw. The generated overloads are left to
`subscribe_event`, whose config type differs per event.

Alternatives rejected:

- **Typing only the request, keeping subscriptions manual.** No library state, but the reconnect
  footgun stays and a declaration cannot exist without a session to send it in.
- **Narrowing `EventSubscriptionRequest.config`.** The wire models mirror what VTS accepts and
  `call_api` sends any payload with any message type, so permissiveness belongs to them (ADR-0014);
  the event/config/handler pairing is a typing concern and lives in the generated stub, where it can
  be exact.
- **A second name for the imperative form** (`subscribe_now`). One concept, one verb: the
  declaration object is the concept, and awaiting it is the imperative use.
- **An `unsubscribe_event(data_model)` on the plugin** beside `dispose()`. Two ways to give the same
  thing up, and the model-based one has to guess which declaration of that event is meant.
- **A silently permissive `subscribe_event` fallback.** The overloads end in one generic overload
  for models this package does not model, and its `config` has no default: a fallback that accepted a
  call without one would swallow the missing config of every event whose config model has required
  fields. A wrong config passed on purpose still type-checks there — `Any` accepts it — and VTS
  answers with its own config error, which reaches `on_subscribe_failed`.

## Consequences

- A declaration without a handler is a subscription whose frames are dropped, exactly as a manual
  subscription was; the two halves are still separate concepts, only their declaration is not.
- Re-subscribing resets per-subscription state at VTS, and the events that count their pushes
  (`ArtMeshTrackingEventData.event_counter`) count from zero again after every reconnect — including
  when a declaration is re-sent and then re-sent again by an `on_authenticated` handler that carries
  a fresher config.
- `plugin.subscriptions` is public, so a plugin can look up what it has declared.
- Disposing of a registration drops it from the registry, so a frame already in flight finds nothing
  to dispatch to; a handler cannot be running from a registration that is gone.
