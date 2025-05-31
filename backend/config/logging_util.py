# backend/config/logging.py
import logging
import sys
import structlog

# Import processor formatter for stdlib compatibility
from structlog.stdlib import ProcessorFormatter

# Import project settings
from config.settings import settings


def setup_logging():
    # Read log level from env
    log_level = settings.LOG_LEVEL.upper()

    # Processors shared between stdlib and structlog logs
    shared_processors = [
        structlog.contextvars.merge_contextvars,         # Merge context variables into the log
        structlog.processors.StackInfoRenderer(),        # Render stack information
        structlog.dev.set_exc_info,                      # Add exc_info to log records if present
        structlog.stdlib.add_log_level,                  # Add log level to event dict
        structlog.stdlib.add_logger_name,                # Add logger name to event dict
        structlog.stdlib.PositionalArgumentsFormatter(), # Apply %-style formatting for stdlib logs
        structlog.processors.TimeStamper(                # Add timestamp to logs
            fmt="%Y-%m-%d %H:%M:%S", utc=False           # fmt="iso", utc=True
        ),
        structlog.processors.UnicodeDecoder(),           # Decode bytes to unicode
        structlog.processors.ExceptionPrettyPrinter() if settings.environment == "development" else structlog.processors.format_exc_info,   # Pretty print exceptions
        structlog.processors.CallsiteParameterAdder(
            parameters={
                        # structlog.processors.CallsiteParameter.FILENAME, 
                        # structlog.processors.CallsiteParameter.FUNC_NAME, 
                        structlog.processors.CallsiteParameter.LINENO, 
                        structlog.processors.CallsiteParameter.MODULE, 
                        structlog.processors.CallsiteParameter.PATHNAME, 
                        # structlog.processors.CallsiteParameter.PROCESS, 
                        structlog.processors.CallsiteParameter.PROCESS_NAME, 
                        # structlog.processors.CallsiteParameter.THREAD, 
                        structlog.processors.CallsiteParameter.THREAD_NAME}, 
            additional_ignores=None
        ),                                                 # Add callsite parameters
    ]

    # Renderer: Console for development, JSON for production
    renderer = (
        structlog.dev.ConsoleRenderer()
        if settings.environment == "development"
        else structlog.processors.JSONRenderer()
    )

    # Formatter for stdlib logs, uses the shared processors and the renderer
    formatter = ProcessorFormatter(
        processor=renderer,                  # Final processor (how logs are rendered)
        foreign_pre_chain=shared_processors  # Pre-processors for non-structlog logs (e.g., FastAPI/Uvicorn)
    )

    # Stream handler for stdout with processor-aware formatter
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)          # Apply the processor-based formatter

    # Root logger config (affects all standard loggers including FastAPI/Uvicorn)
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    root_logger.handlers.clear()             # Clear default handlers
    root_logger.addHandler(handler)  # Add our custom handler

    # Final structlog configuration
    structlog.configure(
        processors=[
            *shared_processors,                          # Apply same processors to structlog logs
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,  # Prepare for ProcessorFormatter rendering
        ],
        context_class=dict,                              # Use plain dict for context
        logger_factory=structlog.stdlib.LoggerFactory(), # Use stdlib-compatible logger factory
        wrapper_class=structlog.stdlib.BoundLogger,      # BoundLogger for log method bindings
        cache_logger_on_first_use=True                   # Cache logger instances
    )

# Utility to get a logger instance (named after caller module if not provided)
def get_logger(name: str = None):
    if name is None:
        try:
            frame = sys._getframe(1)  # Caller’s frame
            name = frame.f_globals.get("__name__", "app")
        except (ValueError, AttributeError, KeyError):
            name = "app"
    return structlog.get_logger(name)

# Call setup_logging() when this module is imported
setup_logging()
