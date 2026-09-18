# coovts Guide

> [简体中文](../zh-cn/README.md)

coovts is an async Python client for the VTube Studio plugin API. One `Plugin` object owns a single
WebSocket connection and is responsible for the authentication handshake, for correlating requests
with their responses, and for dispatching the events VTube Studio pushes to your code.

## Mental model

- **One `Plugin` is one connection.** The connection lifecycle (connect → authenticate → receive →
  drop → reconnect) runs in a supervisor task the library owns; your code watches it through
  **hooks** instead of managing a socket.
- **Two ways in and out of VTS:** requests (`call_api` / `send_request`) and events (a subscription
  plus a handler).
- **The library does not mirror VTS state.** Model lists, parameter values and subscription state
  are asked for when needed; the connection state machine is the only local state it keeps.

## Reading order

| #   | Page                                          | Read it when                                                            |
| --- | --------------------------------------------- | ----------------------------------------------------------------------- |
| 1   | [Getting started](./01-getting-started.md)    | You want it running once, and need to know where the token goes         |
| 2   | [Connection and lifecycle](./02-lifecycle.md) | You need hook timing, reconnect semantics, or where to init per session |
| 3   | [Requests](./03-requests.md)                  | Timeouts, exceptions, field naming, endpoints nobody modelled yet       |
| 4   | [Events](./04-events.md)                      | How subscriptions relate to handlers, and how dispatch behaves          |
| 5   | [When things fail](./05-failures.md)          | Which layer raises, what gets retried, what is worth retrying           |

## Three conventions

1. **Terminology follows [`CONTEXT.md`](../../../CONTEXT.md).** Plugin, hook, handler, subscription and
   pending request all mean there what they mean here.
2. **This guide only documents what reading the code does not tell you.** Every request and event
   field is documented upstream, in the [request reference][req] and the [event reference][evt]; we
   do not repeat it, we point at it.
3. **Reasons live in [`docs/adr/`](../../adr/).** This guide says what the behaviour is; link out to an
   ADR when you want to know why it is that way.

Upstream links are pinned to the sync commit recorded in [`docs/references.md`](../../references.md),
so they do not rot as upstream moves.

[req]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/README.md
[evt]: https://github.com/DenchiSoft/VTubeStudio/blob/0f46ef44b487fa17c8120db572ebd925924b93a3/Events/README.md
