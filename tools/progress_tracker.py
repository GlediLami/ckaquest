#!/usr/bin/env python3
"""
K8sQuest Progress Tracker
Displays completion status of all 50 levels
"""

import json
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()

WORLDS = {
    "world-1-basics": {
        "name": "World 1: Core Kubernetes Basics",
        "levels": list(range(1, 11)),
        "total_xp": 1450,
        "difficulty": "Beginner"
    },
    "world-2-deployments": {
        "name": "World 2: Deployments & Scaling",
        "levels": list(range(11, 21)),
        "total_xp": 2000,
        "difficulty": "Intermediate"
    },
    "world-3-networking": {
        "name": "World 3: Networking & Services",
        "levels": list(range(21, 31)),
        "total_xp": 2300,
        "difficulty": "Intermediate"
    },
    "world-4-storage": {
        "name": "World 4: Storage & Stateful Apps",
        "levels": list(range(31, 41)),
        "total_xp": 2600,
        "difficulty": "Advanced"
    },
    "world-5-security": {
        "name": "World 5: Security & Production Ops",
        "levels": list(range(41, 51)),
        "total_xp": 3150,
        "difficulty": "Advanced"
    }
}

def load_progress():
    """Load progress from progress.json"""
    progress_file = Path("progress.json")
    if progress_file.exists():
        with open(progress_file, encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "total_xp": 0}

def count_available_levels(world_dir):
    """Count how many levels exist in a world directory"""
    world_path = Path("worlds") / world_dir
    if not world_path.exists():
        return 0

    # Count directories with mission.yaml
    count = 0
    for item in world_path.iterdir():
        if item.is_dir() and (item / "mission.yaml").exists():
            count += 1
    return count

def main():
    console.clear()

    progress = load_progress()
    completed_levels = progress.get("completed", [])
    total_xp = progress.get("total_xp", 0)

    # Header
    console.print(Panel.fit(
        "[bold cyan]🎮 K8sQuest - Progress Tracker[/bold cyan]\n"
        f"[yellow]Total XP:[/yellow] {total_xp:,} / 11,500\n"
        f"[yellow]Levels Completed:[/yellow] {len(completed_levels)} / 50",
        border_style="cyan"
    ))

    console.print()

    # World-by-world breakdown
    for world_dir, world_info in WORLDS.items():
        # Count available and completed levels
        available_count = count_available_levels(world_dir)
        total_levels = len(world_info["levels"])

        # Count completed levels in this world
        completed_in_world = sum(
            1 for level in completed_levels
            if level.startswith(world_dir)
        )

        # Status icon
        if available_count == 0:
            status = "⏳"
            status_text = "Blueprint Only"
            color = "yellow"
        elif available_count == total_levels:
            status = "✅"
            status_text = "Complete"
            color = "green"
        else:
            status = "🚧"
            status_text = "In Progress"
            color = "cyan"

        # World header
        console.print(f"\n{status} [{color}]{world_info['name']}[/{color}]")
        console.print(f"   Difficulty: {world_info['difficulty']} | XP: {world_info['total_xp']:,}")

        # Progress bar
        if available_count > 0:
            progress_pct = (completed_in_world / available_count) * 100
            console.print(f"   Available: {available_count}/{total_levels} levels | Completed: {completed_in_world}/{available_count}")

            # Visual progress bar
            bar_length = 40
            filled = int((completed_in_world / available_count) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            console.print(f"   [{color}]{bar}[/{color}] {progress_pct:.0f}%")
        else:
            console.print(f"   Status: {status_text}")

    console.print()

    # Overall progress
    total_available = sum(count_available_levels(w) for w in WORLDS.keys())
    overall_pct = (len(completed_levels) / total_available) * 100 if total_available > 0 else 0

    console.print(Panel.fit(
        f"[bold]Overall Progress:[/bold] {len(completed_levels)}/{total_available} levels ({overall_pct:.1f}%)\n"
        f"[bold]Implementation Status:[/bold] {total_available}/50 levels created ({(total_available/50)*100:.0f}%)",
        title="Summary",
        border_style="green"
    ))

    # Next steps
    if total_available < 50:
        console.print("\n[yellow]📝 Next Steps:[/yellow]")
        for world_dir, world_info in WORLDS.items():
            available = count_available_levels(world_dir)
            total = len(world_info["levels"])
            if available < total:
                remaining = total - available
                console.print(f"  • {world_info['name']}: Create {remaining} more level(s)")
                break

if __name__ == "__main__":
    main()
