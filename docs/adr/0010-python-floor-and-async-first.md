# Python 3.12 floor, asynchronous end to end

**Status**: accepted

`requires-python = ">=3.12"` is a hard requirement, not a soft preference: the code uses PEP 695
syntax throughout — `type X = ...` aliases, `class Hook[T]`, generic functions and
`def f[**P, R]` — and none of it parses on 3.11. Everything the library exposes to user code is
asynchronous: hooks, handlers and `call_api` are all coroutines. `run_sync` is the single bridge
offered to blocking code, wrapping a synchronous callable into an awaitable executed in an executor.

The choice is partly habit: this library grew out of nonebot2 plugin code, where handlers are
async. It is also the right fit — a plugin talks to VTube Studio constantly, and async is better
than sync for frequent I/O — and asynchronous code is inherently easier to write than the
synchronous multi-threaded equivalent a single shared socket would otherwise need. Rather than ship
both an async core and a blocking façade that reimplements it, the library commits to one model and
lets callers wrap individual blocking functions at the edges.

## Consequences

- Python 3.11 and older are unsupported, so users on an older interpreter cannot install the
  library at all rather than failing later at runtime.
- The PEP 695 surface syntax means every `type` alias and generic class must stay inside a runtime
  scope supported by 3.12; helper modules cannot be back-ported for older interpreters.
- Blocking work (file I/O, controller polling, image encoding) belongs on the caller's side of
  `run_sync`, and thread safety of the wrapped callable is the caller's problem.
