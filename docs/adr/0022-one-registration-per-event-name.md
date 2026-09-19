---
status: accepted
amends: ['0017']
---

# One registration per event name, completed by the first model

ADR-0017 gives an event one `EventRegistration`: the record of its data model, the config its
subscription carries, and its handlers. Which of the two ways of declaring an event came first
decided what that record could do, and the difference was silent.

An event named by its wire name has no model to decode with, so its handlers get the payload as it
arrived and its subscription carries an empty config. Declaring the same event by its data model
afterwards found the existing registration and returned it unchanged: the model was dropped, so the
handlers stayed on the raw payload, and `subscribe` read the absent model as "no config model" and
subscribed with `{}` — the empty config a named declaration is allowed to have, and a silently wrong
one for an event whose config model declares fields.

The first model now completes the registration. `registration()` upgrades a model-less registration
when a model arrives for the same event name, and takes over the empty config that declaration left
behind, so the order of the two declarations stops mattering: the event is subscribed to the same way
and decoded the same way whichever declaration came first. A config a caller passed explicitly is not
touched, because that is a choice rather than a default. Handlers attached before the model arrived
keep the payload they were promised, because a handler carries the model it decodes with rather than
reading the registration's.

A second _different_ model naming the same event is refused with `ValueError`. Two models cannot
decode one event, and picking one of them quietly is what the old behavior did.

## Consequences

- The registry stays one registration per event name, so `plugin.subscriptions` still enumerates what
  a plugin declared, and `dispose()` still gives up the whole event.
- Declaring by name and never by model is unchanged: nothing is decoded, and the config stays empty.
- `msg_t`, a model's escape hatch, is what makes two models collide, and the refusal names both.
- A model arriving late can fail where the name could not: an event whose config model has a required
  field raises the same `ValueError` `subscribe()` raises, at the declaration that brought the model.

Alternatives rejected: two registrations per name, one raw and one modelled, which splits dispatch and
disposal across two records for one event; letting a later model replace an earlier one, which
re-decodes handlers that were attached on purpose on the raw payload; and letting a later declaration
replace a config a caller passed explicitly, which is not what declaring a default means.
