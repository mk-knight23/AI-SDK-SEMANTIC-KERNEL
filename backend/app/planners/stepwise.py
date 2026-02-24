"""
Stepwise planner for Semantic Kernel.

Implements a stepwise planning approach where the AI plans
one step at a time, re-evaluating after each step.
"""

import json
from typing import Any, Dict, List, Optional, TypedDict
from dataclasses import dataclass, field

from semantic_kernel import Kernel
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase

from app.memory.store import MemoryStore, get_memory_store


@dataclass
class PlanStep:
    """A single step in a plan."""
    function: str
    plugin: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    description: str = ""


@dataclass
class Plan:
    """A plan containing multiple steps."""
    goal: str
    steps: List[PlanStep] = field(default_factory=list)
    status: str = "pending"  # pending, in_progress, completed, failed
    current_step: int = 0
    result: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "goal": self.goal,
            "steps": [
                {
                    "function": s.function,
                    "plugin": s.plugin,
                    "parameters": s.parameters,
                    "description": s.description
                }
                for s in self.steps
            ],
            "status": self.status,
            "current_step": self.current_step,
            "result": self.result
        }


class StepwisePlanner:
    """
    Stepwise planner for Semantic Kernel.

    Plans one step at a time, re-evaluating after each step.
    This is useful for complex, multi-step tasks.
    """

    def __init__(
        self,
        kernel: Kernel,
        memory_store: Optional[MemoryStore] = None,
        service_id: Optional[str] = None
    ):
        """
        Initialize the stepwise planner.

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
        Create a stepwise plan for the given goal.

        Args:
            goal: The goal to achieve
            context: Optional context string
            available_functions: List of available functions

        Returns:
            Plan with initial steps
        """
        # Build function descriptions
        function_list = self._build_function_list(available_functions)

        # Create prompt for planning
        prompt = self._build_planning_prompt(goal, context, function_list)

        # Get initial plan from AI
        try:
            result = await self.kernel.invoke_prompt(
                prompt=prompt,
                service_id=self.service_id
            )

            plan_text = str(result)

            # Parse the plan
            steps = self._parse_plan(plan_text)

            return Plan(
                goal=goal,
                steps=steps,
                status="pending"
            )

        except Exception as e:
            # Return a simple plan if AI planning fails
            return Plan(
                goal=goal,
                steps=[],
                status="failed"
            )

    async def execute_plan(
        self,
        plan: Plan,
        max_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Execute a plan step by step.

        Args:
            plan: Plan to execute
            max_steps: Maximum number of steps to execute

        Returns:
            Execution result
        """
        plan.status = "in_progress"
        results = []

        for i in range(min(max_steps, len(plan.steps))):
            plan.current_step = i
            step = plan.steps[i]

            try:
                # Execute the step
                result = await self._execute_step(step)
                results.append({
                    "step": i,
                    "function": f"{step.plugin}.{step.function}",
                    "result": result
                })

                # Check if we're done
                if self._is_goal_complete(plan.goal, result):
                    plan.status = "completed"
                    plan.result = result
                    break

            except Exception as e:
                results.append({
                    "step": i,
                    "function": f"{step.plugin}.{step.function}",
                    "error": str(e)
                })

        if plan.status == "in_progress":
            plan.status = "completed" if results else "failed"
            plan.result = json.dumps(results, indent=2)

        return {
            "plan": plan.to_dict(),
            "results": results
        }

    async def think_and_act(
        self,
        goal: str,
        context: Optional[str] = None,
        available_functions: Optional[List[Dict[str, Any]]] = None,
        max_iterations: int = 5
    ) -> Dict[str, Any]:
        """
        Think, plan, and act iteratively.

        This is the main stepwise planning loop:
        1. Analyze the current state
        2. Decide on the next action
        3. Execute the action
        4. Repeat until goal is achieved

        Args:
            goal: The goal to achieve
            context: Optional context
            available_functions: List of available functions
            max_iterations: Maximum thinking iterations

        Returns:
            Final result and execution history
        """
        function_list = self._build_function_list(available_functions)
        history = []
        current_context = context or ""

        for i in range(max_iterations):
            # Build thinking prompt
            prompt = self._build_thinking_prompt(
                goal,
                current_context,
                history,
                function_list
            )

            try:
                # Get AI decision
                result = await self.kernel.invoke_prompt(
                    prompt=prompt,
                    service_id=self.service_id
                )

                decision = str(result)
                action = self._parse_action(decision)

                if action.get("done"):
                    return {
                        "status": "completed",
                        "goal": goal,
                        "result": action.get("result"),
                        "iterations": i + 1,
                        "history": history
                    }

                # Execute the action
                if action.get("function"):
                    step_result = await self._execute_function(
                        action["plugin"],
                        action["function"],
                        action.get("parameters", {})
                    )

                    history.append({
                        "iteration": i,
                        "action": action,
                        "result": step_result
                    })

                    current_context += f"\nAction {i}: {action.get('description', '')}\nResult: {step_result}"

            except Exception as e:
                history.append({
                    "iteration": i,
                    "error": str(e)
                })

        return {
            "status": "max_iterations_reached",
            "goal": goal,
            "history": history
        }

    def _build_function_list(
        self,
        available_functions: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """Build a formatted list of available functions."""
        if not available_functions:
            # Get functions from kernel
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

    def _build_planning_prompt(
        self,
        goal: str,
        context: Optional[str],
        function_list: str
    ) -> str:
        """Build the planning prompt."""
        prompt = f"""You are an AI planner. Create a step-by-step plan to achieve the following goal:

Goal: {goal}

{"Context: " + context if context else ""}

Available functions:
{function_list}

Create a plan with 3-5 steps. For each step, specify:
1. The function to call (in format: plugin.function)
2. Required parameters
3. A brief description

Format your response as:
Step 1: [description]
Function: plugin.function
Parameters: {{"param": "value"}}

Step 2: ...
"""
        return prompt

    def _build_thinking_prompt(
        self,
        goal: str,
        context: str,
        history: List[Dict[str, Any]],
        function_list: str
    ) -> str:
        """Build the thinking prompt for iterative planning."""
        history_str = json.dumps(history[-3:], indent=2) if history else "No previous actions"

        prompt = f"""You are an AI agent working towards a goal.

Goal: {goal}

Current context:
{context}

Recent action history:
{history_str}

Available functions:
{function_list}

Decide on the next action. If the goal is achieved, respond with:
DONE: [final result]

Otherwise, respond with:
Action: [description of what to do]
Function: plugin.function
Parameters: {{"param": "value"}}
"""
        return prompt

    def _parse_plan(self, plan_text: str) -> List[PlanStep]:
        """Parse a plan from AI response."""
        steps = []

        lines = plan_text.split("\n")
        current_step = None

        for line in lines:
            line = line.strip()
            if line.lower().startswith("step"):
                if current_step:
                    steps.append(current_step)
                current_step = PlanStep(function="", plugin="", description=line)
            elif line.lower().startswith("function:") and current_step:
                parts = line[9:].strip().split(".")
                if len(parts) == 2:
                    current_step.plugin = parts[0]
                    current_step.function = parts[1]
            elif line.lower().startswith("parameters:") and current_step:
                try:
                    params = json.loads(line[11:].strip())
                    current_step.parameters = params
                except:
                    pass

        if current_step and current_step.function:
            steps.append(current_step)

        return steps

    def _parse_action(self, decision: str) -> Dict[str, Any]:
        """Parse an action decision from AI response."""
        decision = decision.strip()

        if decision.upper().startswith("DONE:"):
            return {
                "done": True,
                "result": decision[5:].strip()
            }

        action = {
            "done": False,
            "function": None,
            "plugin": None,
            "parameters": {},
            "description": ""
        }

        for line in decision.split("\n"):
            line = line.strip()
            if line.lower().startswith("action:"):
                action["description"] = line[7:].strip()
            elif line.lower().startswith("function:"):
                parts = line[9:].strip().split(".")
                if len(parts) == 2:
                    action["plugin"] = parts[0]
                    action["function"] = parts[1]
            elif line.lower().startswith("parameters:"):
                try:
                    action["parameters"] = json.loads(line[11:].strip())
                except:
                    pass

        return action

    async def _execute_step(self, step: PlanStep) -> str:
        """Execute a single plan step."""
        return await self._execute_function(
            step.plugin,
            step.function,
            step.parameters
        )

    async def _execute_function(
        self,
        plugin: str,
        function: str,
        parameters: Dict[str, Any]
    ) -> str:
        """Execute a kernel function."""
        try:
            # Get the function from kernel
            kernel_func = self.kernel.plugins.get(plugin, {}).get(function)

            if kernel_func:
                result = await kernel_func(**parameters)
                return str(result)
            else:
                return f"Function {plugin}.{function} not found"

        except Exception as e:
            return f"Error executing {plugin}.{function}: {str(e)}"

    def _is_goal_complete(self, goal: str, result: str) -> bool:
        """Check if the goal has been achieved."""
        # Simple heuristic: if result is substantive and error-free
        if "error" in result.lower() or "not found" in result.lower():
            return False

        return len(result) > 10


# Global planner factory
def create_stepwise_planner(
    kernel: Kernel,
    memory_store: Optional[MemoryStore] = None
) -> StepwisePlanner:
    """
    Create a stepwise planner instance.

    Args:
        kernel: Semantic Kernel instance
        memory_store: Optional memory store

    Returns:
        StepwisePlanner instance
    """
    return StepwisePlanner(kernel, memory_store)
