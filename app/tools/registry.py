
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from pydantic import BaseModel


class ToolNotFoundError(ValueError):
    pass


@dataclass(frozen=True)
class ToolDefinition:
    name: str
    description: str
    function: Callable[..., Any]
    input_model: type[BaseModel]


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        function: Callable[..., Any],
        input_model: type[BaseModel],
    ) -> None:
        if name in self._tools:
            raise ValueError(f"Tool '{name}' is already registered.")

        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            function=function,
            input_model=input_model,
        )

    def get(self, name: str) -> ToolDefinition:
        try:
            return self._tools[name]
        except KeyError as exc:
            raise ToolNotFoundError(
                f"Tool '{name}' is not registered."
            ) from exc

    def list_tools(self) -> list[str]:
        return sorted(self._tools)

    def describe_tools(self) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_model.model_json_schema(),
            }
            for tool in (
                self._tools[name] for name in sorted(self._tools)
            )
        ]