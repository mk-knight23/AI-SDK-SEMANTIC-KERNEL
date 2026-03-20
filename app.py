"""Production-style Semantic Kernel runtime for Kazi's Agents Army."""

from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent / "core"))
from agents_army_core import MissionRequest, build_mission_plan, render_system_instructions


def run_semantic_kernel_mission(mission_text: str) -> dict:
    plan = build_mission_plan(MissionRequest(mission_text))
    instructions = render_system_instructions(plan)

    try:
        import semantic_kernel as sk
    except Exception as exc:
        return {
            "primary": plan.primary,
            "support": plan.support,
            "result": None,
            "verification": f"Semantic Kernel dependency missing: {exc}",
        }

    _ = sk.Kernel()
    return {
        "primary": plan.primary,
        "support": plan.support,
        "result": instructions,
        "verification": "Semantic Kernel initialization succeeded.",
    }
