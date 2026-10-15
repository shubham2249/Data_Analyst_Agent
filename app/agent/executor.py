
from typing import Any

from pydantic import ValidationError

from app.tools.registry import ToolRegistry


class ToolExecutionError(RuntimeError):
    pass


class ToolExecutor:
    def __init__(self, registry: ToolRegistry):
        self.registry = registry

    def execute(
        self,
        tool_name: str,
        arguments: dict[str, Any],
        *,
        context: dict[str, Any] | None = None,
    ) -> Any:
        definition = self.registry.get(tool_name)

        try:
            validated = definition.input_model.model_validate(arguments)
        except ValidationError as exc:
            raise ToolExecutionError(
                f"Invalid arguments for '{tool_name}'."
            ) from exc

        execution_arguments = validated.model_dump()
        execution_arguments.update(context or {})

        try:
            return definition.function(**execution_arguments)
        except (ValueError, KeyError, TypeError) as exc:
            raise ToolExecutionError(
                f"Tool '{tool_name}' could not complete the operation."
            ) from exc