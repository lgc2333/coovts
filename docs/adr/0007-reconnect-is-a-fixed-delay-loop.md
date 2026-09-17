# Reconnection is an unconditional fixed-delay loop

**Status**: accepted

One supervisor task loops forever: connect, authenticate, receive until the socket fails, sleep
`reconnect_delay` (5 seconds by default), repeat. There is no exponential backoff, no jitter and no
attempt limit, and a failed connect or a failed authentication sleeps for the same fixed delay in
the same loop.

The expected deployment is a plugin running beside a desktop application that the user starts and
stops whenever they like. Retrying at a constant rate keeps the "start the plugin, then start
VTube Studio" case working without any configuration, and a delay long enough to be polite costs
nothing when nothing else is happening.

## Consequences

- VTube Studio closed for hours is retried every 5 seconds for hours. That traffic is accepted.
- Recovery is not transparent to user code. Authentication is re-established and `on_authenticated`
  fires again, so anything that must exist per session — event subscriptions, parameter creation —
  belongs in that hook, not in `main()`.
- Pending requests are cancelled on disconnect (see ADR-0008), so reconnect never resumes work that
  was in flight.
