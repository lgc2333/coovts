from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cookit.loguru import (
        log_exception_warning as log_exception_warning,
        logged_suppress as logged_suppress,
        warning_suppress as warning_suppress,
    )
    from loguru import logger as logger

else:
    try:
        from loguru import logger as logger

        if True:  # prevent unsorted imports warn
            from cookit.loguru import (
                log_exception_warning as log_exception_warning,
                logged_suppress as logged_suppress,
                warning_suppress as warning_suppress,
            )
    except ImportError:
        from contextlib import contextmanager
        from typing import Any

        class _DummyLogger:
            def __getattr__(self, name: str):
                def _dummy(*_args, **_kwargs):
                    return _DummyLogger()

                return _dummy

        logger = _DummyLogger()

        @contextmanager
        def logged_suppress(_msg: Any = None, *excs, **_kwargs):
            try:
                yield
            except Exception as e:
                if excs and not isinstance(e, excs):
                    raise
                return

        warning_suppress = logged_suppress

        def log_exception_warning(*_args, **_kwargs):
            pass
