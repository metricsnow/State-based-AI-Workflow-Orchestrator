"""
Schema utility functions for workflow events.

Provides utilities for JSON schema generation and validation.
"""

import json
from typing import Dict, Any

from .schema import WorkflowEvent


def generate_json_schema(mode: str = "validation") -> Dict[str, Any]:
    """Generate JSON schema for WorkflowEvent model.

    Args:
        mode: Schema mode - 'validation' or 'serialization'

    Returns:
        JSON schema dictionary

    Example:
        >>> schema = generate_json_schema()
        >>> print(json.dumps(schema, indent=2))
    """
    return WorkflowEvent.model_json_schema(mode=mode)


def save_json_schema(filepath: str, mode: str = "validation") -> None:
    """Save JSON schema to file.

    Args:
        filepath: Path to save JSON schema file
        mode: Schema mode - 'validation' or 'serialization'

    Example:
        >>> save_json_schema("workflow_event_schema.json")
    """
    schema = generate_json_schema(mode=mode)
    with open(filepath, "w") as f:
        json.dump(schema, f, indent=2)


def get_validation_schema() -> Dict[str, Any]:
    """Get JSON schema for validation (input schema).

    Returns:
        JSON schema dictionary for validation
    """
    return generate_json_schema(mode="validation")


def get_serialization_schema() -> Dict[str, Any]:
    """Get JSON schema for serialization (output schema).

    Returns:
        JSON schema dictionary for serialization
    """
    return generate_json_schema(mode="serialization")

