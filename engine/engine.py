#!/usr/bin/env python3
"""
CKAQuest - CKA exam training game, based on K8sQuest.
Every level breaks or asks for something on a real 3-node cluster.
"""

import json
import os
import select
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

import yaml
from rich import box
from rich.console import Console
from rich.live import Live
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt
from rich.table import Table
from rich.text import Text

import re
import termios
import tty

# Import retro UI components
try:
    from retro_ui import (
        celebrate_milestone,
        show_command_menu,
        show_game_complete,
        show_level_start,
        show_power_up_notification,
        show_retro_header,
        show_retro_welcome,
        show_victory,
        show_xp_bar,
    )

    RETRO_UI_ENABLED = True
except ImportError:
    RETRO_UI_ENABLED = False
    print("ℹ️  Retro UI not available, using standard interface")

# Import player name generator
try:
    from player_name import get_player_name
except ImportError:

    def get_player_name(console, current_name=None):
        from rich.prompt import Prompt

        return Prompt.ask("Enter your name", default="K8s Explorer")


# Isolation: the game only ever talks to its own cluster through its own kubeconfig.
# It never reads or writes ~/.kube/config.
CQ_ROOT = Path(__file__).resolve().parent.parent
CQ_HOME = Path(os.environ.get("CQ_HOME", Path.home() / ".ckaquest"))
CQ_WORK = Path(os.environ.get("CQ_WORK", Path.home() / "ckaquest-work"))
CQ_CONTEXT = "kind-" + os.environ.get("CQ_CLUSTER", "ckaquest")
DEFAULT_NAMESPACE = "ckaquest"
os.environ["KUBECONFIG"] = os.environ.get(
    "CKAQUEST_KUBECONFIG", str(CQ_HOME / "kubeconfig")
)
os.environ.setdefault("CQ_ROOT", str(CQ_ROOT))
os.environ.setdefault("CQ_WORK", str(CQ_WORK))

CKA_DOMAINS = {
    "troubleshooting": "Troubleshooting (30%)",
    "architecture": "Cluster Architecture, Installation & Configuration (25%)",
    "networking": "Services & Networking (20%)",
    "workloads": "Workloads & Scheduling (15%)",
    "storage": "Storage (10%)",
}


def natural_sort_key(path):
    """Sort level-2 before level-10"""
    return [int(p) if p.isdigit() else p.lower() for p in re.split(r"(\d+)", path.name)]


def discover_worlds():
    """All world directories in order. New worlds show up without code changes."""
    worlds_dir = CQ_ROOT / "worlds"
    return [
        d for d in sorted(worlds_dir.iterdir(), key=natural_sort_key)
        if d.is_dir() and d.name.startswith("world-")
    ]


def discover_levels(world_path):
    return [
        d for d in sorted(world_path.iterdir(), key=natural_sort_key)
        if d.is_dir() and (d / "mission.yaml").exists()
    ]


def level_namespace(mission):
    return mission.get("namespace", DEFAULT_NAMESPACE)


def script_env(mission=None):
    """Environment for setup/validate/cleanup scripts"""
    env = dict(os.environ)
    env["NAMESPACE"] = level_namespace(mission or {})
    env["PATH"] = f"{CQ_ROOT / 'bin' / 'shims'}:{CQ_ROOT / 'bin'}:{env.get('PATH', '')}"
    return env


console = Console()


def wait_for_any_key():
    """Block until the user presses any single key (including space bar)."""
    fd = sys.stdin.fileno()
    try:
        old_settings = termios.tcgetattr(fd)
    except termios.error:
        input()  # fallback (e.g. piped stdin)
        return
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        # Consume the rest of an escape sequence so it doesn't pollute input
        if ch == "\x1b" and select.select([sys.stdin], [], [], 0.05)[0]:
            sys.stdin.read(2)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        try:
            termios.tcflush(fd, termios.TCIFLUSH)
        except Exception:
            pass


class PaginatedDisplay:
    """Helper class for paginating long content like man pages"""

    def __init__(self, console, lines_per_page=None):
        self.console = console
        self.lines_per_page = lines_per_page or self._calculate_lines_per_page()

    def _calculate_lines_per_page(self):
        """Pick a sensible default based on terminal height"""
        default_height = 24
        try:
            size = getattr(self.console, "size", None)
            if size and getattr(size, "height", None):
                default_height = size.height
            elif hasattr(self.console, "height"):
                default_height = self.console.height
        except Exception:
            pass
        # Reserve space for title, borders, and navigation prompts
        return max(8, default_height - 8)

    def _get_keypress(self):
        """Read a single keypress and return it"""
        if True:
            fd = sys.stdin.fileno()
            old_settings = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    # Arrow/Page keys send an escape sequence quickly; detect extra bytes
                    if select.select([sys.stdin], [], [], 0.01)[0]:
                        sys.stdin.read(2)
                        return ""
                    # Treat a lone ESC as a quick exit request
                    return 'q'
                # Convert carriage return to newline (Enter key in raw mode)
                if ch == "\r":
                    return "\n"
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
                try:
                    termios.tcflush(fd, termios.TCIFLUSH)
                except Exception:
                    pass

    @staticmethod
    def _build_code_block_states(lines):
        """Track whether each line is inside a fenced code block"""
        states = []
        inside_code = False
        for line in lines:
            states.append(inside_code)
            stripped = line.strip()
            if stripped.startswith("```"):
                inside_code = not inside_code
        return states

    def _build_page_ranges(self, lines):
        """Create page ranges that avoid splitting fenced code blocks"""
        if not lines:
            return [(0, 0)]

        code_states = self._build_code_block_states(lines)
        ranges = []
        start = 0
        line_count = len(lines)

        while start < line_count:
            end = min(start + self.lines_per_page, line_count)
            # Avoid splitting inside a code block by extending to the closing fence
            while end < line_count and code_states[end - 1]:
                end += 1
            if end == start:  # Safety: ensure progress
                end = min(start + self.lines_per_page, line_count)
            ranges.append((start, end))
            start = end

        return ranges

    def _render_page(self, page_content, title, border_style, page_num=None, total_pages=None):
        # Use Rich's terminal controls so escape sequences don't leak into output.
        self.console.clear()

        if page_num is not None and total_pages is not None:
            page_indicator = f" [Page {page_num}/{total_pages}]"
        else:
            page_indicator = ""

        self.console.print(
            Panel(
                Markdown(page_content),
                title=f"[bold {border_style}]{title}{page_indicator}[/bold {border_style}]",
                border_style=border_style,
                box=box.DOUBLE,
            )
        )

    def _print_navigation_hint(self, page_index, total_pages):
        nav_parts = ["[dim]Navigation:[/dim]", "[cyan]Enter/Space[/cyan] next"]
        if page_index > 0:
            nav_parts.append("[cyan]b[/cyan] back")
        if total_pages > 1:
            nav_parts.append("[cyan]g[/cyan] go to start")
        nav_parts.append("[cyan]q[/cyan] skip debrief")
        if page_index == total_pages - 1:
            nav_parts.append("[cyan]Enter[/cyan] finishes")
        hint = " • ".join(nav_parts)
        self.console.print(hint)

    def display_paginated(self, content, title="Content", border_style="green", use_alt_buffer=False):
        """Display content with pagination like man pages
        
        Args:
            content: The content to display
            title: Title for the panel
            border_style: Color/style of the border
            use_alt_buffer: If True, use alternative screen buffer (content disappears after exit)
                          If False, content stays in terminal history (better for learning content)
        """
        lines = content.split('\n')
        page_ranges = self._build_page_ranges(lines)
        total_pages = len(page_ranges)

        if total_pages == 1:
            self._render_page(content, title, border_style)
            self.console.print()
            Prompt.ask("\n[dim]Press ENTER to continue[/dim]", default="")
            return

        # Optionally enter alternative screen buffer (like less/man pages)
        # For debriefs, we want content to stay visible in terminal history
        if use_alt_buffer:
            sys.stdout.write("\033[?1049h")  # Enable alternative buffer
            sys.stdout.flush()

        try:
            page_index = 0

            while True:
                start_idx, end_idx = page_ranges[page_index]
                page_content = '\n'.join(lines[start_idx:end_idx])
                self._render_page(page_content, title, border_style, page_index + 1, total_pages)
                self.console.print()
                self._print_navigation_hint(page_index, total_pages)

                key = self._get_keypress()
                if not key:
                    continue

                key_lower = key.lower()
                if key in ('\n', ' ', ''):
                    if page_index == total_pages - 1:
                        break
                    page_index = min(total_pages - 1, page_index + 1)
                elif key_lower == 'b' and page_index > 0:
                    page_index -= 1
                elif key_lower == 'g':
                    page_index = 0
                elif key_lower == 'q':
                    # Skip remaining pages
                    break
                else:
                    # Unrecognized input - ignore and wait again
                    continue
        finally:
            # Exit alternative screen buffer if it was enabled
            if use_alt_buffer:
                sys.stdout.write("\033[?1049l")  # Disable alternative buffer
                sys.stdout.flush()

        self.console.print()


class CKAQuest:
    def __init__(self):
        self.base_dir = CQ_ROOT
        self.progress_file = self.base_dir / "progress.json"
        self.progress = self.load_progress()

    def load_progress(self):
        """Load player progress from JSON file"""
        if self.progress_file.exists():
            with open(self.progress_file, "r", encoding='utf-8', errors='replace') as f:
                progress = json.load(f)
                # Ensure current_level exists for resume functionality
                if "current_level" not in progress:
                    progress["current_level"] = None
                return progress
        return {
            "total_xp": 0,
            "completed_levels": [],
            "current_world": "world-1-basics",
            "current_level": None,
            "player_name": "Padawan",
        }

    def save_progress(self):
        """Save player progress"""
        with open(self.progress_file, "w", encoding='utf-8') as f:
            json.dump(self.progress, indent=2, fp=f)

    def show_welcome(self):
        """Display welcome screen with retro gaming style"""
        if RETRO_UI_ENABLED:
            show_retro_welcome()
            time.sleep(1)

        console.clear()

        title = """
   ██████╗██╗  ██╗ █████╗  ██████╗ ██╗   ██╗███████╗███████╗████████╗
  ██╔════╝██║ ██╔╝██╔══██╗██╔═══██╗██║   ██║██╔════╝██╔════╝╚══██╔══╝
  ██║     █████╔╝ ███████║██║   ██║██║   ██║█████╗  ███████╗   ██║
  ██║     ██╔═██╗ ██╔══██║██║▄▄ ██║██║   ██║██╔══╝  ╚════██║   ██║
  ╚██████╗██║  ██╗██║  ██║╚██████╔╝╚██████╔╝███████╗███████║   ██║
   ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚══▀▀═╝  ╚═════╝ ╚══════╝╚══════╝   ╚═╝
"""
        console.print(
            Panel(
                Text(title, style="bold cyan")
                + Text("\nCKA exam training on a real 3-node cluster (Kubernetes v1.37)", style="bold yellow"),
                title="[bold magenta]⚔️  CKAQUEST  ⚔️[/bold magenta]",
                border_style="cyan",
                box=box.HEAVY,
            )
        )
        console.print()

        total = self.total_levels
        done = len(self.progress["completed_levels"])
        completion = (done / total) * 100 if total else 0
        progress_bar = "█" * int(completion / 5) + "░" * (20 - int(completion / 5))
        stats = Table(show_header=False, box=box.HEAVY, border_style="yellow")
        stats.add_column("Stat", style="cyan bold")
        stats.add_column("Value", style="yellow bold")
        stats.add_row("🎮 PLAYER", self.progress["player_name"])
        stats.add_row("💎 TOTAL XP", str(self.progress["total_xp"]))
        stats.add_row("⭐ LEVELS CLEARED", f"{done}/{total}")
        stats.add_row("📊 PROGRESS", f"[{progress_bar}] {completion:.0f}%")
        if self.progress.get("current_level"):
            stats.add_row("🎯 CURRENT MISSION", self.progress["current_level"])
        stats.add_row("☸️  CLUSTER", f"{CQ_CONTEXT} (kubeconfig {os.environ['KUBECONFIG']})")
        console.print(
            Panel(stats, title="[bold yellow]⚡ PLAYER STATUS ⚡[/bold yellow]", border_style="yellow", box=box.HEAVY)
        )
        console.print()

    def load_mission(self, level_path):
        """Load mission metadata"""
        mission_file = level_path / "mission.yaml"
        with open(mission_file, "r", encoding='utf-8', errors='replace') as f:
            return yaml.safe_load(f)

    def show_mission_briefing(self, mission, level_name):
        """Display mission briefing screen"""
        console.clear()

        briefing = f"""
# 🎯 {mission["name"]}

**Mission**: {mission["description"]}

**Objective**: {mission["objective"]}

**XP Reward**: {mission["xp"]} XP
        """

        console.print(
            Panel(
                Markdown(briefing),
                title=f"[bold cyan]Level: {level_name}[/bold cyan]",
                border_style="yellow",
                box=box.DOUBLE,
            )
        )
        console.print()

    def show_progressive_hints(self, level_path, hint_level=1, show_all=False):
        """Show hints progressively - unlock more as players struggle

        Args:
            level_path: Path to the level directory
            hint_level: Current hint level (1-3)
            show_all: If True, show all unlocked hints. If False, show only the current hint level.
        """
        hints_available = []

        for i in range(1, 4):
            hint_file = level_path / f"hint-{i}.txt"
            if hint_file.exists():
                hints_available.append((i, hint_file))

        if not hints_available:
            console.print("[yellow]No hints available for this level[/yellow]")
            return

        # Show header with progress
        console.print(
            Panel(
                f"[bold yellow]💡 Hints (Unlocked: {min(hint_level, len(hints_available))}/{len(hints_available)})[/bold yellow]",
                border_style="yellow",
            )
        )

        if show_all:
            # Show all unlocked hints
            for i, hint_file in hints_available:
                if i <= hint_level:
                    with open(hint_file, "r", encoding='utf-8', errors='replace') as f:
                        hint_content = f.read().strip()

                    hint_style = "cyan" if i == 1 else ("yellow" if i == 2 else "green")
                    console.print(
                        f"\n[bold {hint_style}]Hint {i}:[/bold {hint_style}] {hint_content}"
                    )
                else:
                    console.print(
                        f"\n[dim]Hint {i}: 🔒 Locked - try again to unlock[/dim]"
                    )
        else:
            # Show only the current hint level (newest unlocked hint)
            if hint_level <= len(hints_available):
                i, hint_file = hints_available[hint_level - 1]
                with open(hint_file, "r", encoding='utf-8', errors='replace') as f:
                    hint_content = f.read().strip()

                hint_style = (
                    "cyan"
                    if hint_level == 1
                    else ("yellow" if hint_level == 2 else "green")
                )
                console.print(
                    f"\n[bold {hint_style}]Hint {hint_level}:[/bold {hint_style}] {hint_content}"
                )

                # Show status of other hints
                for j in range(1, len(hints_available) + 1):
                    if j < hint_level:
                        console.print(
                            f"\n[dim]Hint {j}: ✅ Previously unlocked (type 'hints' to see all)[/dim]"
                        )
                    elif j > hint_level:
                        console.print(
                            f"\n[dim]Hint {j}: 🔒 Locked - try again to unlock[/dim]"
                        )
            else:
                console.print("\n[yellow]All hints have been unlocked![/yellow]")
                console.print("[dim]Type 'hints' again to see all hints[/dim]")

        console.print()
        return min(hint_level, len(hints_available))

    def show_debrief(self, level_path):
        """Show the post-mission debrief with learning explanations"""
        debrief_file = level_path / "debrief.md"

        if not debrief_file.exists():
            console.print("[yellow]No debrief available for this level[/yellow]")
            return

        with open(debrief_file, "r", encoding='utf-8', errors='replace') as f:
            debrief_content = f.read()

        # Use paginated display WITHOUT alternative buffer
        # This keeps the debrief visible in terminal history for reference
        paginator = PaginatedDisplay(console)
        paginator.display_paginated(
            debrief_content,
            title="🎓 Mission Debrief - What You Learned",
            border_style="green",
            use_alt_buffer=False  # Keep debrief in terminal history
        )

    def get_completed_debriefs(self):
        """Return completed levels that have a debrief, in level order."""
        completed_levels = set(self.progress.get("completed_levels", []))
        debriefs = [
            (level.name, level)
            for _, level in self.all_levels()
            if level.name in completed_levels and (level / "debrief.md").exists()
        ]
        return debriefs

    def review_completed_debriefs(self):
        """Let the player revisit debriefs from completed levels."""
        debriefs = self.get_completed_debriefs()
        if not debriefs:
            console.print("\n[yellow]No completed mission debriefs are available yet.[/yellow]\n")
            return

        while True:
            console.clear()
            console.print(
                Panel(
                    "[bold cyan]Review the learning notes from missions you have cleared.[/bold cyan]",
                    title="[bold green]Completed Mission Debriefs[/bold green]",
                    border_style="green",
                )
            )
            for index, (level_name, level_path) in enumerate(debriefs, start=1):
                mission = self.load_mission(level_path)
                console.print(f"  [{index:2d}] {mission.get('name', level_name)}")
            console.print("  [q] Return to the main menu\n")

            choice = Prompt.ask(
                "Choose a debrief",
                choices=[str(index) for index in range(1, len(debriefs) + 1)] + ["q"],
                default="q",
            )
            if choice == "q":
                return

            _, level_path = debriefs[int(choice) - 1]
            self.show_debrief(level_path)

    def show_solution_file(self, level_path):
        """Display the solution.yaml file contents"""
        solution_file = level_path / "solution.yaml"

        if not solution_file.exists():
            console.print("[yellow]No solution file available for this level[/yellow]")
            return

        with open(solution_file, "r", encoding='utf-8', errors='replace') as f:
            solution_content = f.read()

        console.print(
            Panel(
                f"[cyan]{solution_content}[/cyan]",
                title="[bold green]📄 solution.yaml[/bold green]",
                border_style="green",
                box=box.ROUNDED,
            )
        )
        console.print()

    # ------------------------------------------------------------------
    # Level content
    # ------------------------------------------------------------------

    def show_task(self, mission):
        """The exam-style task. This is what you would read in the real exam."""
        task = mission.get("task")
        if not task:
            return
        domain = CKA_DOMAINS.get(mission.get("domain", ""), "")
        body = task.strip()
        if mission.get("docs"):
            body += "\n\n**Docs you may open in the exam:**\n" + "\n".join(
                f"- {link}" for link in mission["docs"]
            )
        console.print(
            Panel(
                Markdown(body),
                title=f"[bold magenta]📝 Exam task[/bold magenta]  [dim]{domain}[/dim]",
                border_style="magenta",
                box=box.HEAVY,
            )
        )
        console.print()

    def show_solution_file(self, level_path):
        """Display the reference solution (solution.yaml or solution.md)"""
        for name in ("solution.md", "solution.yaml"):
            solution_file = level_path / name
            if solution_file.exists():
                content = solution_file.read_text(encoding="utf-8", errors="replace")
                body = Markdown(content) if name.endswith(".md") else f"[cyan]{content}[/cyan]"
                console.print(
                    Panel(
                        body,
                        title=f"[bold green]📄 {name}[/bold green]",
                        border_style="green",
                        box=box.ROUNDED,
                    )
                )
                console.print()
                return
        console.print("[yellow]No solution file available for this level[/yellow]")

    def show_guide(self, level_path):
        """Step-by-step guide: guide.md, then SOLUTION.md, then all hints"""
        for name in ("guide.md", "SOLUTION.md"):
            guide = level_path / name
            if guide.exists():
                PaginatedDisplay(console).display_paginated(
                    guide.read_text(encoding="utf-8", errors="replace"),
                    title="📖 Guide",
                    border_style="green",
                )
                return
        self.show_progressive_hints(level_path, hint_level=3, show_all=True)

    # ------------------------------------------------------------------
    # Cluster interaction
    # ------------------------------------------------------------------

    def get_resource_status(self, namespace):
        """One-line summary of resources in the level namespace"""
        result = subprocess.run(
            ["kubectl", "get", "pods,deploy,svc,pvc", "-n", namespace,
             "--no-headers", "--request-timeout=3s"],
            capture_output=True, text=True, timeout=6,
        )
        if result.returncode != 0:
            return "API not reachable" if "refused" in result.stderr else "Checking..."
        lines = [line.split()[:3] for line in result.stdout.strip().splitlines() if line.strip()]
        if not lines:
            return f"No resources in namespace {namespace}"
        return " | ".join(" ".join(parts[:2]) for parts in lines[:4])

    def show_terminal_instructions(self, mission):
        namespace = level_namespace(mission)
        console.print(
            Panel(
                Text.from_markup(
                    "[bold yellow]📟 WORK IN A SECOND TERMINAL[/bold yellow]\n\n"
                    f"  source {CQ_ROOT}/env.sh\n\n"
                    "[cyan]That terminal now talks only to the CKAQuest cluster.[/cyan]\n"
                    f"• Namespace for this level: [bold]{namespace}[/bold]\n"
                    "• Nodes: [bold]ssh controlplane[/bold], [bold]ssh node01[/bold], [bold]ssh node02[/bold]\n"
                    f"• Files you are asked to write go to [bold]{CQ_WORK}[/bold]\n"
                    "• Come back here and choose [bold]validate[/bold] when done"
                ),
                title="[bold red]⚠️  YOUR WORKSPACE[/bold red]",
                border_style="red",
                box=box.DOUBLE,
            )
        )
        console.print()

    def monitor_status(self, mission, duration=10):
        """Monitor resource status in real-time"""
        namespace = level_namespace(mission)
        console.print(f"\n[yellow]👀 Watching namespace {namespace} for {duration} seconds...[/yellow]\n")
        status_table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan")
        status_table.add_column("Time", style="dim")
        status_table.add_column("Status", style="yellow")
        with Live(status_table, refresh_per_second=2, console=console):
            for _ in range(duration):
                try:
                    status = self.get_resource_status(namespace)
                except subprocess.TimeoutExpired:
                    status = "Timeout (is the API server down?)"
                status_table.add_row(datetime.now().strftime("%H:%M:%S"), status)
                time.sleep(1)
        console.print()

    def preflight(self):
        """Make sure the CKAQuest cluster is reachable before touching anything"""
        kubeconfig = Path(os.environ["KUBECONFIG"])
        if not kubeconfig.exists():
            console.print(f"[red]⚠️  No CKAQuest kubeconfig at {kubeconfig}.[/red]")
            console.print("[yellow]Run ./install.sh (or bin/cq-cluster up) first.[/yellow]")
            return False
        ctx = subprocess.run(
            ["kubectl", "config", "current-context"], capture_output=True, text=True
        ).stdout.strip()
        if ctx != CQ_CONTEXT:
            subprocess.run(["kubectl", "config", "use-context", CQ_CONTEXT], capture_output=True)
        check = subprocess.run(
            ["kubectl", "--context", CQ_CONTEXT, "get", "--raw=/readyz", "--request-timeout=5s"],
            capture_output=True, text=True,
        )
        if check.returncode != 0:
            console.print("\n[red]⚠️  Cannot reach the CKAQuest API server:[/red]")
            console.print(f"[dim red]{check.stderr.strip()}[/dim red]")
            console.print("[yellow]If a previous level broke the control plane, fix it or run:[/yellow]")
            console.print("[dim]    bin/cq-cluster rebuild[/dim]")
            return False
        return True

    def run_level_script(self, level_path, name, mission, timeout=600):
        script = level_path / name
        if not script.exists():
            return None
        return subprocess.run(
            ["bash", name],
            cwd=str(level_path),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            env=script_env(mission),
            timeout=timeout,
        )

    def cleanup_level(self, level_path, mission):
        """Undo what a level changed outside its namespace (nodes, cluster-scoped objects)"""
        if (level_path / "cleanup.sh").exists():
            console.print("[dim]🧹 Restoring the cluster after this level...[/dim]")
            result = self.run_level_script(level_path, "cleanup.sh", mission)
            if result and result.returncode != 0:
                console.print(f"[yellow]Cleanup reported a problem:[/yellow]\n[dim]{result.stdout}{result.stderr}[/dim]")
        namespace = level_namespace(mission)
        if namespace not in (DEFAULT_NAMESPACE, "default", "kube-system"):
            # Free the RAM. --wait=false so the next level does not wait for it.
            subprocess.run(
                ["kubectl", "delete", "namespace", namespace, "--ignore-not-found", "--wait=false"],
                capture_output=True, text=True,
            )
        if self.progress.get("dirty_level") == str(level_path.relative_to(CQ_ROOT)):
            self.progress["dirty_level"] = None
            self.save_progress()

    def cleanup_dirty_level(self):
        """A previous session quit in the middle of a level: restore the cluster first"""
        dirty = self.progress.get("dirty_level")
        if not dirty:
            return
        level_path = CQ_ROOT / dirty
        if level_path.exists():
            self.cleanup_level(level_path, self.load_mission(level_path))
        self.progress["dirty_level"] = None
        self.save_progress()

    def reset_namespace(self, namespace):
        """Remove leftovers from earlier levels in a shared namespace"""
        subprocess.run(
            ["kubectl", "label", "namespace", namespace,
             "pod-security.kubernetes.io/enforce-", "pod-security.kubernetes.io/audit-",
             "pod-security.kubernetes.io/warn-"],
            capture_output=True, text=True,
        )
        subprocess.run(
            ["kubectl", "delete",
             "all,cm,secret,pvc,netpol,ing,role,rolebinding,sa,quota,limits,hpa,pdb",
             "--all", "-n", namespace, "--ignore-not-found", "--timeout=90s"],
            capture_output=True, text=True,
        )

    def ensure_addons(self, mission):
        for addon in mission.get("requires", []):
            if addon in ("ingress", "gateway"):
                console.print(f"[yellow]Installing add-on '{addon}' (first time only)...[/yellow]")
                result = subprocess.run(
                    [str(CQ_ROOT / "bin" / "cq-cluster"), "addon", addon],
                    capture_output=True, text=True,
                )
                if result.returncode != 0:
                    console.print(f"[red]Add-on install failed:[/red]\n[dim]{result.stdout}{result.stderr}[/dim]")
                    return False
        return True

    def deploy_mission(self, level_path, mission):
        """Prepare the level: clean up, then break things (or set up the task)"""
        console.print("\n[yellow]🚀 Deploying mission environment...[/yellow]")
        self.cleanup_dirty_level()
        if not self.preflight():
            return False
        if not self.ensure_addons(mission):
            return False

        namespace = level_namespace(mission)
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("Cleaning up...", total=3)
            # Clean state first, also for a level replayed after a quit
            self.run_level_script(level_path, "cleanup.sh", mission)
            if namespace == DEFAULT_NAMESPACE:
                subprocess.run(["kubectl", "create", "namespace", namespace], capture_output=True, text=True)
                self.reset_namespace(namespace)
            else:
                # Own namespace per level: start from an empty one, also on a replay
                subprocess.run(
                    ["kubectl", "delete", "namespace", namespace, "--ignore-not-found", "--timeout=120s"],
                    capture_output=True, text=True,
                )
                subprocess.run(["kubectl", "create", "namespace", namespace], capture_output=True, text=True)
            progress.advance(task)

            progress.update(task, description="Deploying the scenario...")
            self.progress["dirty_level"] = str(level_path.relative_to(CQ_ROOT))
            self.save_progress()
            # setup.sh prepares the cluster (nodes, history, files), then broken.yaml is applied
            result = self.run_level_script(level_path, "setup.sh", mission)
            if (result is None or result.returncode == 0) and (level_path / "broken.yaml").exists():
                result = subprocess.run(
                    ["kubectl", "apply", "-f", str(level_path / "broken.yaml")],
                    capture_output=True, text=True, env=script_env(mission),
                )
            if result.returncode != 0:
                console.print("[red]Setup failed:[/red]")
                console.print(f"[dim red]{result.stderr}[/dim red]")
                if result.stdout:
                    console.print(f"[dim]{result.stdout}[/dim]")
                return False
            progress.update(task, description="✅ Environment ready!")
            progress.advance(task, 2)

        console.print()
        console.print(
            Panel(
                Text("🔴 MISSION DEPLOYED 🔴", style="bold red", justify="center")
                + Text(f"\n\n{mission['description']}", style="yellow", justify="center"),
                border_style="red",
                box=box.DOUBLE,
            )
        )
        console.print()
        return True

    def validate_mission(self, level_path, mission):
        """Run validation script and show results"""
        console.print("\n[yellow]🔍 Validating your solution...[/yellow]\n")
        try:
            result = self.run_level_script(level_path, "validate.sh", mission, timeout=300)
        except subprocess.TimeoutExpired:
            console.print("[red]Validation timed out (is the API server up?)[/red]")
            return False
        output = result.stdout if result else "validate.sh missing"
        if result and result.stderr and result.returncode != 0:
            output += f"\n{result.stderr}"
        ok = result is not None and result.returncode == 0
        console.print(
            Panel(
                Text("✅ MISSION COMPLETE! ✅" if ok else "❌ Not quite there yet...",
                     style="bold green" if ok else "bold red", justify="center")
                + Text(f"\n\n{output}", style="green" if ok else "red"),
                border_style="green" if ok else "red",
                box=box.DOUBLE if ok else box.ROUNDED,
            )
        )
        return ok

    # ------------------------------------------------------------------
    # Game loop
    # ------------------------------------------------------------------

    def play_level(self, level_path):
        """Play a single level. Returns False when the player wants to stop."""
        level_name = level_path.name
        mission = self.load_mission(level_path)

        if RETRO_UI_ENABLED:
            match = re.search(r"level-(\d+)", level_name)
            show_level_start(
                int(match.group(1)) if match else 0,
                mission["name"],
                mission["xp"],
                mission.get("difficulty", "beginner"),
            )
            wait_for_any_key()

        console.clear()
        if RETRO_UI_ENABLED:
            console.print(show_retro_header(mission["name"], mission["xp"], self.progress["total_xp"]))
            console.print()

        difficulty_colors = {"beginner": "green", "intermediate": "yellow", "advanced": "red", "expert": "magenta"}
        difficulty_icons = {"beginner": "⚡", "intermediate": "⚡⚡", "advanced": "⚡⚡⚡", "expert": "💀"}
        difficulty = mission.get("difficulty", "beginner")
        diff_color = difficulty_colors.get(difficulty, "cyan")
        metadata = f"[{diff_color}]{difficulty_icons.get(difficulty, '⚡')}[/{diff_color}] {difficulty.upper()}"
        metadata += f"  |  ⏱️  ~{mission.get('expected_time', '?')}"
        if mission.get("domain") in CKA_DOMAINS:
            metadata += f"  |  📚 {CKA_DOMAINS[mission['domain']]}"
        if "concepts" in mission:
            metadata += f"\n🎯 {', '.join(mission['concepts'])}"
        console.print(Panel(metadata, border_style=diff_color, box=box.HEAVY))
        console.print()

        self.show_mission_briefing(mission, level_name)

        if not self.deploy_mission(level_path, mission):
            console.print("\n[red]⚠️  Mission deployment failed![/red]")
            if Confirm.ask("Skip this level?", default=False):
                return True
            return False

        self.show_task(mission)
        self.show_terminal_instructions(mission)

        current_hint_level = 0
        attempts = 0
        actions = ["check", "task", "hints", "guide", "solution", "validate", "reset", "skip", "quit"]
        while True:
            console.print()
            if RETRO_UI_ENABLED:
                console.print(show_command_menu())
            console.print()
            try:
                action = Prompt.ask("⚔️  Choose your action", choices=actions, default="validate")
            except EOFError:
                return False

            if action == "check":
                self.monitor_status(mission, duration=10)

            elif action == "task":
                self.show_mission_briefing(mission, level_name)
                self.show_task(mission)

            elif action == "hints":
                current_hint_level += 1
                if RETRO_UI_ENABLED:
                    show_power_up_notification("hint")
                console.print()
                self.show_progressive_hints(level_path, current_hint_level, show_all=False)

            elif action == "guide":
                if RETRO_UI_ENABLED:
                    show_power_up_notification("guide")
                self.show_guide(level_path)

            elif action == "solution":
                if RETRO_UI_ENABLED:
                    show_power_up_notification("solution")
                self.show_solution_file(level_path)

            elif action == "reset":
                if Confirm.ask("Restore and re-deploy this level from scratch?", default=False):
                    self.cleanup_level(level_path, mission)
                    if not self.deploy_mission(level_path, mission):
                        return False
                    self.show_task(mission)

            elif action == "validate":
                attempts += 1
                console.print(f"\n[dim]⚔️  ATTEMPT #{attempts}[/dim]")
                if self.validate_mission(level_path, mission):
                    xp_earned = mission["xp"]
                    first_clear = level_name not in self.progress["completed_levels"]
                    if first_clear:
                        self.progress["total_xp"] += xp_earned
                        self.progress["completed_levels"].append(level_name)
                    self.save_progress()
                    if RETRO_UI_ENABLED:
                        show_victory(xp_earned if first_clear else 0, self.progress["total_xp"])
                    else:
                        console.print(f"\n[bold yellow]🌟 +{xp_earned if first_clear else 0} XP! Total: {self.progress['total_xp']} XP[/bold yellow]")
                    console.print(f"[dim]⚡ Cleared in {attempts} attempt(s)[/dim]\n")

                    if RETRO_UI_ENABLED:
                        completed_count = len(self.progress["completed_levels"])
                        if completed_count == self.total_levels:
                            show_game_complete()
                        elif completed_count == self.total_levels // 2:
                            celebrate_milestone("halfway")

                    self.show_debrief(level_path)
                    self.cleanup_level(level_path, mission)
                    console.print("\n[dim]Press Enter to continue...[/dim]")
                    input()
                    return Confirm.ask("Ready for the next challenge?", default=True)

                current_hint_level = min(current_hint_level + 1, 3)
                console.print("\n[yellow]Read the failed checks above, then fix and validate again.[/yellow]\n")

            elif action == "skip":
                if Confirm.ask("Skip this level? (No XP will be awarded)", default=False):
                    self.cleanup_level(level_path, mission)
                    return True

            elif action == "quit":
                console.print(
                    "\n[yellow]👋 Progress saved. The level stays deployed. "
                    "It is cleaned up when you start the next one.[/yellow]\n"
                )
                sys.exit(0)

    def all_levels(self):
        return [(world, level) for world in discover_worlds() for level in discover_levels(world)]

    @property
    def total_levels(self):
        return len(self.all_levels())

    def play_from(self, start_level=None):
        """Play levels in order, starting at start_level (a level dir name) or the beginning"""
        levels = self.all_levels()
        start = 0
        if start_level:
            for i, (_, level) in enumerate(levels):
                if level.name == start_level:
                    start = i + 1 if start_level in self.progress["completed_levels"] else i
                    break
        for world, level in levels[start:]:
            self.progress["current_level"] = level.name
            self.progress["current_world"] = world.name
            self.save_progress()
            if not self.play_level(level):
                return

    COURSE_SECTIONS = {
        1: "Introduction", 2: "Core Concepts", 3: "Scheduling", 4: "Logging & Monitoring",
        5: "Application Lifecycle Management", 6: "Cluster Maintenance", 7: "Security", 8: "Storage",
        9: "Networking", 10: "Design and Install a Cluster", 11: "Install the kubeadm way",
        12: "Helm Basics", 13: "Kustomize Basics", 14: "Troubleshooting", 15: "Other Topics",
    }

    def play_by_section(self):
        """Play the levels that belong to one course section, in order"""
        console.clear()
        console.print(Panel("[bold cyan]Play by Course Section[/bold cyan]\n[dim]Watch a section of the course, then play its levels[/dim]", border_style="cyan"))
        by_section = {}
        for world, level in self.all_levels():
            sec = self.load_mission(level).get("course_section")
            if sec:
                by_section.setdefault(int(sec), []).append((world, level))
        for sec, title in self.COURSE_SECTIONS.items():
            levels = by_section.get(sec, [])
            done = sum(1 for _, l in levels if l.name in self.progress["completed_levels"])
            count = f"{done}/{len(levels)} done" if levels else "no levels yet"
            console.print(f"  [{sec:2d}] {title} [dim]{count}[/dim]", markup=True)
        console.print("\n[dim]Enter section number or 'q' to go back[/dim]\n")
        choice = Prompt.ask("Section", default="q")
        if choice.lower() == "q":
            return
        if not choice.isdigit() or not by_section.get(int(choice)):
            console.print("[red]No levels for that section[/red]")
            time.sleep(1)
            return self.play_by_section()
        for world, level in by_section[int(choice)]:
            if level.name in self.progress["completed_levels"]:
                continue
            self.progress["current_level"] = level.name
            self.progress["current_world"] = world.name
            self.save_progress()
            if not self.play_level(level):
                return
        console.print(f"\n[green]Section {choice} cleared.[/green]")

    def play_specific_level(self):
        """Pick a level from the full list"""
        console.clear()
        console.print(Panel("[bold cyan]Select a Level to Play[/bold cyan]", border_style="cyan"))
        choices = []
        current_world = None
        for world, level in self.all_levels():
            if world != current_world:
                current_world = world
                title = world.name.replace("world-", "World ").replace("-", " ").title()
                console.print(f"\n[bold yellow]{title}[/bold yellow]")
            mission = self.load_mission(level)
            status = "✅" if level.name in self.progress["completed_levels"] else "⭕"
            domain = mission.get("domain", "")
            choices.append((world, level))
            console.print(f"  [{len(choices):2d}] {status} {mission.get('name', level.name)} [dim]{domain}[/dim]", markup=True)

        console.print("\n[dim]Enter level number or 'q' to go back[/dim]\n")
        choice = Prompt.ask("Choose a level", default="q")
        if choice.lower() == "q":
            return
        if not choice.isdigit() or not 1 <= int(choice) <= len(choices):
            console.print("[red]Invalid level number[/red]")
            time.sleep(1)
            return self.play_specific_level()

        world, level = choices[int(choice) - 1]
        self.progress["current_level"] = level.name
        self.progress["current_world"] = world.name
        self.save_progress()
        if not self.play_level(level):
            return
        console.print("\n[cyan]What next?[/cyan]")
        console.print("  [1] Pick another level", markup=False)
        console.print("  [2] Continue in order from here", markup=False)
        console.print("  [q] Quit", markup=False)
        next_choice = Prompt.ask("Your choice", choices=["1", "2", "q"], default="q")
        if next_choice == "1":
            self.play_specific_level()
        elif next_choice == "2":
            self.play_from(level.name)


def main():
    game = CKAQuest()

    if game.progress["player_name"] == "Padawan":
        console.print()
        game.progress["player_name"] = get_player_name(console)
        game.save_progress()
        console.print(f"\n[green]✨ Welcome, {game.progress['player_name']}![/green]\n")
        time.sleep(1)

    game.show_welcome()

    while True:
        has_progress = bool(game.progress["completed_levels"]) or game.progress.get("current_level")
        console.print("[cyan]Choose an option:[/cyan]")
        if has_progress:
            console.print("  [1] Continue where you left off", markup=False)
        else:
            console.print("  [1] Start from level 1", markup=False)
        console.print("  [2] Play a specific level", markup=False)
        console.print("  [3] Play by course section", markup=False)
        console.print("  [4] Start over (reset progress)", markup=False)
        menu_choices = ["1", "2", "3", "4"]
        if game.get_completed_debriefs():
            console.print("  [5] Review completed mission debriefs", markup=False)
            menu_choices.append("5")
        console.print("  [q] Quit", markup=False)
        console.print()
        choice = Prompt.ask("Your choice", choices=menu_choices + ["q"], default="1")

        if choice == "1":
            game.play_from(game.progress.get("current_level"))
        elif choice == "2":
            game.play_specific_level()
        elif choice == "3":
            game.play_by_section()
        elif choice == "4":
            if Confirm.ask("Really reset all progress?", default=False):
                game.progress.update(current_level=None, completed_levels=[], total_xp=0)
                game.save_progress()
                game.play_from(None)
        elif choice == "5":
            game.review_completed_debriefs()
            continue
        console.print(f"\n[yellow]See you later, {game.progress['player_name']}![/yellow]\n")
        return


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[yellow]👋 Game interrupted. Progress saved![/yellow]\n")
        sys.exit(0)
    except EOFError:
        sys.exit(0)
    except Exception as e:
        console.print(f"\n[bold red]Fatal error:[/bold red] {e}")
        import traceback
        console.print(f"[dim]{traceback.format_exc()}[/dim]")
        sys.exit(1)
