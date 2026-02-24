"""
Sequential planner for Semantic Kernel.

Implements a sequential planning approach where the AI creates
a complete plan upfront, then executes all steps.
"""

import json
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field

from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments

from app.memory.store import MemoryStore, get_memory_store
from app.planners.stepwise import PlanStep, Plan


class SequentialPlanner:
    """
    Sequential planner for Semantic Kernel.

    Creates a complete plan upfront, then executes all steps in sequence.
    This is useful when the full path to the goal is clear.
    """

    def __init__(
        self,
        kernel: Kernel,
        memory_store: Optional[MemoryStore] = None,
        service_id: Optional[str] = None
    ):
        """
        Initialize the sequential planner.

        Args:
            kernel: Semantic Kernel instance
            memory_store: Optional memory store for context
            service_id: Optional service ID for chat completion
        """
        self.kernel = kernel
        self.memory_store = memory_store or get_memory_store()
        self.service_id = service_id or "openai"

    async def create_plan(
        self,
        goal: str,
        context: Optional[str] = None,
        available_functions: Optional[List[Dict[str, Any]]] = None
    ) -> Plan:
        """
        Create a complete sequential plan.

        Args:
            goal: The goal to achieve
            context: Optional context string
            available_functions: List of available functions

        Returns:
            Complete Plan with all steps
        """
        function_list = self._build_function_list(available_functions)

        prompt = f"""You are an AI planner. Create a complete step-by-step plan to achieve this goal:

Goal: {goal}

{"Context: " + context if context else ""}

Available functions:
{function_list}

Create a comprehensive plan with all necessary steps. Format as JSON:
{{
    "steps": [
        {{
            "function": "plugin.function",
            "parameters": {{"key": "value"}},
            "description": "What this step does"
        }}
    ]
}}
"""

        try:
            result = await self.kernel.invoke_prompt(
                prompt=prompt,
                service_id=self.service_id
            )

            plan_text = str(result)

            # Try to extract JSON
            json_start = plan_text.find("{")
            json_end = plan_text.rfind("}") + 1

            if json_start >= 0 and json_end > json_start:
                json_str = plan_text[json_start:json_end]
                plan_data = json.loads(json_str)

                steps = []
                for step_data in plan_data.get("steps", []):
                    parts = step_data.get("function", ".").split(".")
                    if len(parts) == 2:
                        steps.append(PlanStep(
                            plugin=parts[0],
                            function=parts[1],
                            parameters=step_data.get("parameters", {}),
                            description=step_data.get("description", "")
                        ))

                return Plan(
                    goal=goal,
                    steps=steps,
                    status="pending"
                )

        except Exception as e:
            pass

        # Fallback: return empty plan
        return Plan(goal=goal, steps=[], status="failed")

    async def execute_plan(
        self,
        plan: Plan,
        stop_on_error: bool = False
    ) -> Dict[str, Any]:
        """
        Execute a complete sequential plan.

        Args:
            plan: Plan to execute
            stop_on_error: Whether to stop execution on first error

        Returns:
            Execution results
        """
        plan.status = "in_progress"
        results = []

        for i, step in enumerate(plan.steps):
            plan.current_step = i

            try:
                result = await self._execute_function(
                    step.plugin,
                    step.function,
                    step.parameters
                )

                results.append({
                    "step": i,
                    "function": f"{step.plugin}.{step.function}",
                    "description": step.description,
                    "result": result,
                    "success": True
                })

            except Exception as e:
                results.append({
                    "step": i,
                    "function": f"{step.plugin}.{step.function}",
                    "description": step.description,
                    "error": str(e),
                    "success": False
                })

                if stop_on_error:
                    plan.status = "failed"
                    break

        # Determine final status
        if plan.status != "failed":
            if all(r.get("success", False) for r in results):
                plan.status = "completed"
            else:
                plan.status = "partial"

        plan.result = json.dumps(results, indent=2)

        return {
            "plan": plan.to_dict(),
            "results": results
        }

    def _build_function_list(
        self,
        available_functions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build a formatted list of available functions."""
        if not available_functions:
            available_functions = []
            for plugin_name, plugin in self.kernel.plugins.items():
                for func_name, func in plugin.items():
                    available_functions.append({
                        "plugin": plugin_name,
                        "function": func_name,
                        "description": getattr(func, "__doc__", func_name)
                    })

        formatted = []
        for func in available_functions:
            formatted.append(
                f"- {func['plugin']}.{func['function']}: {func.get('description', '')}"
            )

        return "\n".join(formatted) if formatted else "No functions available"

    async def _execute_function(
        self,
        plugin: str,
        function: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Execute a kernel function."""
        try:
            kernel_func = self.kernel.plugins.get(plugin, {}).get(function)

            if kernel_func:
                result = await kernel_func(**parameters)
                return str(result)
            else:
                return f"Function {plugin}.{function} not found"

        except Exception as e:
            return f"Error: {str(e)}"


def create_sequential_planner(
    kernel: Kernel,
    memory_store: Optional[MemoryStore] = None
) -> SequentialPlanner:
    """
    Create a sequential planner instance.

    Args:
        kernel: Semantic Kernel instance
        memory_store: Optional memory store

    Returns:
        SequentialPlanner instance
    """
    return SequentialPlanner(kernel, memory_store)
