---
status: accepted
amended_by: ['0019']
---

# Reconnection is an unconditional fixed-delay loop

One supervisor task loops forever: connect, authenticate, receive until the socket fails, sleep
`reconnect_delay` (5 seconds by default), repeat. There is no exponential backoff, no jitter and no
attempt limit, and a failed connect or a failed authentication sleeps for the same fixed delay in
the same loop.

Backoff, jitter and attempt limits are real logic to write and tune, and none of it buys anything
here: VTube Studio runs on the same machine as the plugin, so an attempt is a loopback call and
retrying costs nothing. The expected deployment is a plugin beside a desktop application that the
user starts and stops whenever they like, and a constant rate keeps the "start the plugin, then
start VTube Studio" case working without any configuration.

## Consequences

- VTube Studio closed for hours is retried every 5 seconds for hours. That traffic is loopback and
  costs nothing, which is why the loop tolerates it.
- Recovery is not transparent to user code. Authentication is re-established and `on_authenticated`
  fires again, so anything that must exist per session — event subscriptions, parameter creation —
  belongs in that hook, not in `main()`.
- Pending requests are cancelled on disconnect (see ADR-0008), so reconnect never resumes work that
  was in flight.
