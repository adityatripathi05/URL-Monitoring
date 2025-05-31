# backend/config/logging.py
import logging
import sys
import structlog
from .settings import settings # Assuming settings.py is in the same directory

def setup_logging():
    log_level_str = settings.LOG_LEVEL.upper()
    log_level = getattr(logging, log_level_str, logging.INFO)

    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info, # Add exc_info to log records if present
        structlog.processors.format_exc_info,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
    ]

    if settings.environment == "development":
        # Pretty, human-readable logs for development
        processors = shared_processors + [
            structlog.dev.ConsoleRenderer(),
        ]
    else:
        # Structured JSON logs for production
        processors = shared_processors + [
            structlog.processors.dict_tracebacks, # Render tracebacks as dicts for JSON
            structlog.processors.JSONRenderer(),
        ]

    structlog.configure(
        processors=processors,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Optional: Configure standard library logging to use structlog processing
    # This helps if third-party libraries use standard logging
    root_logger = logging.getLogger()
    if root_logger.hasHandlers(): # Check if handlers already exist
        root_logger.handlers.clear() # Remove any default handlers

    handler = logging.StreamHandler(sys.stdout)
    # Processors for stdlib messages, ensure they are simple as they might not have all structlog context
    # Using a basic formatter for stdlib, as structlog's processors will handle the main formatting.
    # The key is to ensure stdlib logs are captured and processed by structlog's pipeline if possible,
    # or at least formatted consistently.

    # Create a dedicated formatter for stdlib records processed by structlog
    stdlib_formatter_processors = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta, # Important for stdlib integration
    ]
    if settings.environment == "development":
        stdlib_formatter_processors.append(structlog.dev.ConsoleRenderer())
    else:
        stdlib_formatter_processors.append(structlog.processors.JSONRenderer())

    formatter = structlog.stdlib.ProcessorFormatter.wrap_for_formatter(
        logging.Formatter('%(message)s', datefmt="iso"), # Basic format, actual formatting by structlog processors
        logger=structlog.get_logger("stdlib_compat"), # Dedicated logger for stdlib messages
        processors=stdlib_formatter_processors
    )

    handler.setFormatter(formatter)
    root_logger.addHandler(handler)
    root_logger.setLevel(log_level)

    # Example of how to get a logger instance
    # logger = structlog.get_logger(__name__)
    # logger.info("Structlog logging configured", environment=settings.environment, log_level=log_level_str)

# Call setup when this module is imported (or explicitly call it in main.py startup)
# For now, let's set it up on import.
# setup_logging() # This can cause issues if settings are not yet loaded, better to call explicitly.

# Function to get a logger instance easily
def get_logger(name: str = None):
    # If no name is provided, structlog will try to determine it,
    # or you can default to a specific name or the root logger.
    return structlog.get_logger(name if name else "app")
