"""Application error types."""


class DependencyError(Exception):
    """Raised when a call to an external dependency fails.

    See CONTRIBUTING.md — external-dependency failures must be caught at the
    call site, logged as a structured `dependency_failure` event, and
    re-raised as this type with `raise ... from exc`.
    """
