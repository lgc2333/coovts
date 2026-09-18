# Backlog

Work that is deferred, not excluded. When the guide or an ADR says something is missing, check here
before assuming it was decided against: everything on this page is meant to be built, and each entry
says what would make building it worth while now.

An entry leaves this page when it is built, or moves into an ADR when it is decided against.

## Batch calls, and a parameter keepalive helper

**What**: convenience wrappers for calling several things in one go, and for keeping a
plugin-controlled parameter alive at the rate VTS requires.

**Trigger**: measurement first. "One request that already carries every value" against "send only
when the value changes" decides what the defaults should be, so the helpers wait for those numbers.

## UDP server discovery and `VTubeStudioAPIStateBroadcast`

**What**: discovering the VTS endpoint on port 47779 instead of configuring it by hand, and modelling
the unsolicited state broadcast VTS sends over UDP.

**Trigger**: a plugin that needs it. The WebSocket API works today as long as the endpoint is
configured, which is why this is the only gap in the model set
([ADR-0004](./adr/0004-vts-api-coverage.md)).

## Logging in the library, if it ever needs any

**What**: the library logs nothing and depends on no logging stack — a design position, not a gap:
everything a caller has to know arrives as a hook or an exception
([ADR-0011](./adr/0011-dependency-set.md)). If that position is ever revisited, the candidates are
connect attempts and their outcome, the authentication steps, request send / receive / expiry, frames
dropped for having no handler or no matching request, and handler failures.

**Trigger**: a diagnosis that hooks and exceptions cannot carry. They are designed to be enough, so a
log line would have to earn its way in — and the dependency is already decided: it would be `loguru`.
