import argparse

try:
    from .app import run_semantic_kernel_mission
except ImportError:
    from app import run_semantic_kernel_mission


def demo(mission: str) -> None:
    out = run_semantic_kernel_mission(mission)
    print("[Semantic Kernel] primary:", out.get("primary"))
    print("[Semantic Kernel] support:", out.get("support"))
    print("[Semantic Kernel] result:", out.get("result"))
    print("[Semantic Kernel] verification:", out.get("verification"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mission", default="integrate plugins and enterprise policy")
    args = parser.parse_args()
    demo(args.mission)
