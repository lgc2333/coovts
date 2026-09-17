# One `Plugin` object owns the whole connection

**Status**: accepted

There is exactly one public runtime class. `Plugin` holds the connection, the authentication state,
the hook lists, the event handler table and the pending request table; connecting, authenticating,
receiving, dispatching and reconnecting are all its methods. Lifecycle callbacks are decorated
lists (`Hook[T]`) rather than overridable methods, so several handlers can be registered per
lifecycle moment, in registration order, without subclassing anything.

## Consequences

- There is no composition seam: two plugins are two objects, and code that wants a connection
  without the rest of `Plugin` has nowhere to put it.
- `Plugin` is the centre of gravity of the public API — most of what ADR-0012 calls public hangs
  off this one object.
- Registration is `@plugin.on_<hook>` and `@plugin.handle_event(SomeEventData)`; both decorators
  return the handler unchanged, so handlers stay ordinary functions that can be registered
  elsewhere too.
- Hooks are lists, so registering the same hook twice adds two handlers; there is no way to replace
  or unregister one.
