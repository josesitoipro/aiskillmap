import logging
import traceback
from typing import TYPE_CHECKING

# ---------------------------------------------------------------------------
# TYPE-CHECKING IMPORTS
# ---------------------------------------------------------------------------
# These imports are evaluated only by static type checkers (MyPy, Pyright, etc.).
# They do **not** run at runtime, so they don’t clash with Django’s app-loading
# sequence.

if TYPE_CHECKING:
    from django.http import HttpRequest

class DBHandler(logging.Handler):
    """
    Custom logging handler that writes critical errors to the LogSystem table.

    It expects the request object to be passed in the log record via
    `extra={'request': ...}`. Only logs 500-level errors (e.g.,
    via logger.error or logger.critical).
    """

    @staticmethod
    def get_native_request(request) -> "HttpRequest | None":
        """
        Ensures compatibility between DRF and Django request objects.
        Returns the underlying HttpRequest regardless of source.
        """
        # Import inside the function to avoid touching Django before
        # the app registry is ready.
        from django.http import HttpRequest
        from rest_framework.request import Request as DRFRequest

        if isinstance(request, DRFRequest):
            return request._request  # unwrap
        return request if isinstance(request, HttpRequest) else None

    def emit(self, record: logging.LogRecord) -> None:
        """
        Persist a single ERROR/CRITICAL log into the LogSystem table.

        All imports that need Django's ORM live **inside** this method so they
        run only *after* django.setup() completes and the app registry is ready.
        """
        try:
            # Late imports: defer any Django–ORM dependency until runtime.
            from django.contrib.auth.models import User
            from core.models import LogSystem

            raw_request = getattr(record, "request", None)
            request = self.get_native_request(raw_request)
            user: User | None = getattr(request, "user", None) if request else None

            LogSystem.objects.create(
                user=user if user and user.is_authenticated else None,
                request_path=request.path if request else "",
                request_method=request.method if request else "",
                request_data=(
                    request.POST.dict()
                    if request and request.method in {"POST", "PUT", "PATCH"}
                    else {}
                ),
                logger_name=record.name,
                module=record.module,
                function_name=record.funcName,
                # Prefer the traceback provided by the logging record; fallback
                # to formatting the current exception info.
                traceback=record.exc_text
                or (
                    "".join(traceback.format_exception(*record.exc_info))
                    if record.exc_info
                    else ""
                ),
            )
        # Never let logging failure crash the main application.
        except Exception:
            print("Failed to log to LogSystem:", traceback.format_exc())
