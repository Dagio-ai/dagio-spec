#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "typer",
#     "rich",
#     "platformdirs",
#     "readchar",
# ]
# ///
"""
Specify CLI - Setup tool for Specify projects

Usage:
    uvx specify-cli.py init
    uvx specify-cli.py init .
    uvx specify-cli.py init path/to/workspace


Or install globally:
    uv tool install --from specify-cli.py specify-cli
    specify init
    specify init path/to/workspace
"""

import os
import subprocess
import sys
import shutil
import shlex
import json
import textwrap
from pathlib import Path
from typing import Optional, Tuple

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.text import Text
from rich.live import Live
from rich.align import Align
from rich.table import Table
from rich.tree import Tree
from typer.core import TyperGroup

# For cross-platform keyboard input
import readchar

# Agent configuration with name, folder, install URL, and CLI tool requirement
AGENT_CONFIG = {
    "copilot": {
        "name": "GitHub Copilot",
        "folder": ".github/",
        "install_url": None,  # IDE-based, no CLI check needed
        "requires_cli": False,
    },

    "claude": {
        "name": "Claude Code",
        "folder": ".claude/",
        "install_url": "https://docs.anthropic.com/en/docs/claude-code/setup",
        "requires_cli": True,
    },

    "gemini": {
        "name": "Gemini CLI",
        "folder": ".gemini/",
        "install_url": "https://github.com/google-gemini/gemini-cli",
        "requires_cli": True,
    },

    "cursor-agent": {
        "name": "Cursor",
        "folder": ".cursor/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },

    "qwen": {
        "name": "Qwen Code",
        "folder": ".qwen/",
        "install_url": "https://github.com/QwenLM/qwen-code",
        "requires_cli": True,
    },

    "opencode": {
        "name": "opencode",
        "folder": ".opencode/",
        "install_url": "https://opencode.ai",
        "requires_cli": True,
    },

    "codex": {
        "name": "Codex CLI",
        "folder": ".codex/",
        "install_url": "https://github.com/openai/codex",
        "requires_cli": True,
    },

    "windsurf": {
        "name": "Windsurf",
        "folder": ".windsurf/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },

    "kilocode": {
        "name": "Kilo Code",
        "folder": ".kilocode/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },

    "auggie": {
        "name": "Auggie CLI",
        "folder": ".augment/",
        "install_url": "https://docs.augmentcode.com/cli/setup-auggie/install-auggie-cli",
        "requires_cli": True,
    },

    "codebuddy": {
        "name": "CodeBuddy",
        "folder": ".codebuddy/",
        "install_url": "https://www.codebuddy.ai/cli",
        "requires_cli": True,
    },

    "roo": {
        "name": "Roo Code",
        "folder": ".roo/",
        "install_url": None,  # IDE-based
        "requires_cli": False,
    },

    "q": {
        "name": "Amazon Q Developer CLI",
        "folder": ".amazonq/",
        "install_url": "https://aws.amazon.com/developer/learning/q-developer-cli/",
        "requires_cli": True,
    },

    "amp": {
        "name": "Amp",
        "folder": ".agents/",
        "install_url": "https://ampcode.com/manual#install",
        "requires_cli": True,
    },

}


ARCHITECTURE_TEMPLATE_FILES = [
    "c1-system-context-template.md",
    "c2-container-diagram-template.md",
    "c3-component-diagram-template.md",
    "c4-code-structure-template.md",
    "c5-dynamic-view-template.md",
    "c6-deployment-template.md",
    "c7-tests-template.md",
    "architecture_overview-template.md",
    "architecture_logs-template.md",
    "architecture-template.json",
]


ARCHITECTURE_DIRECTORY_OVERVIEW = textwrap.dedent(
    """\
    # Architecture Directory\n\n    This folder stores the artefacts produced by `/specify.architecture.create` and `/specify.architecture.update`.\n\n    ## Index Files\n    - `architecture_overview.md`: Entry point for the architecture documentation, including the table of contents linking to every view.\n    - `architecture_logs.md`: Versioned change log describing updates recorded in `architecture.json`.\n\n    ## Expected layout\n\n    ```\n    architecture/\n      c1_context/\n        system_context.md\n      c2_containers/\n        containers_overview.md\n        <container-slug>/\n          container_diagram.md\n      c3_components/\n        <container-slug>/\n          components_overview.md\n          <component-slug>/\n            component_diagram.md\n      c4_code/\n        <component-slug>/\n          code_structure.md\n      c5_dynamic_view/\n        view_diagram.md\n      c6_deployment/\n        deployment_diagram.md\n      c7_tests/\n        tests_overview.md\n      architecture_overview.md\n      architecture_logs.md\n      architecture.json\n    ```\n\n    The JSON model (`specs/architecture/architecture.json`) acts as the source of truth and drives the Markdown views. Treat any Markdown edits as projections that must be reconciled back into the JSON model.\n    """
)


ASSET_ENV_VAR = "SPECIFY_ASSETS_DIR"


def _asset_candidates() -> list[Path]:
    candidates: list[Path] = []
    env_dir = os.getenv(ASSET_ENV_VAR)

    if env_dir:
        candidates.append(Path(env_dir).expanduser())

    module_dir = Path(__file__).resolve().parent
    candidates.append(module_dir / "data")

    try:
        candidates.append(Path(__file__).resolve().parents[3])
    except IndexError:
        pass

    return [path for path in candidates if path]


def _asset_path(*parts: str) -> Path:

    for base in _asset_candidates():
        candidate = base.joinpath(*parts)

        if candidate.exists():
            return candidate

    joined = Path(*parts)

    raise FileNotFoundError(
        f"Unable to locate asset '{joined}'. "
        f"Set {ASSET_ENV_VAR} to override the asset directory."
    )


def _sync_directory(src: Path, dest: Path, *, exclude_dirs: set[str] | None = None, exclude_files: set[str] | None = None) -> None:

    if not src.exists():
        raise FileNotFoundError(f"Missing asset source directory: {src}")

    dest.mkdir(parents=True, exist_ok=True)

    for item in src.iterdir():
        if item.is_dir():
            if exclude_dirs and item.name in exclude_dirs:
                continue

            shutil.copytree(item, dest / item.name, dirs_exist_ok=True)

        else:
            if exclude_files and item.name in exclude_files:
                continue

            shutil.copy2(item, dest / item.name)


SCRIPT_TYPE_CHOICES = {"sh": "POSIX Shell (bash/zsh)", "ps": "PowerShell"}

CLAUDE_LOCAL_PATH = Path.home() / ".claude" / "local" / "claude"

BANNER = "DAGIO Specify"
TAGLINE = "Based on GitHub Spec Kit version 0.0.79 - Spec-Driven Development Toolkit (https://github.com/github/spec-kit)"


class StepTracker:
    """Track and render hierarchical steps without emojis, similar to Claude Code tree output.
    Supports live auto-refresh via an attached refresh callback.
    """

    def __init__(self, title: str):
        self.title = title
        self.steps = []  # list of dicts: {key, label, status, detail}
        self.status_order = {"pending": 0, "running": 1,
                             "done": 2, "error": 3, "skipped": 4}
        self._refresh_cb = None  # callable to trigger UI refresh

    def attach_refresh(self, cb):
        self._refresh_cb = cb

    def add(self, key: str, label: str):
        if key not in [s["key"] for s in self.steps]:
            self.steps.append({"key": key, "label": label,
                              "status": "pending", "detail": ""})
            self._maybe_refresh()

    def start(self, key: str, detail: str = ""):
        self._update(key, status="running", detail=detail)

    def complete(self, key: str, detail: str = ""):
        self._update(key, status="done", detail=detail)

    def error(self, key: str, detail: str = ""):
        self._update(key, status="error", detail=detail)

    def skip(self, key: str, detail: str = ""):
        self._update(key, status="skipped", detail=detail)

    def _update(self, key: str, status: str, detail: str):
        for s in self.steps:
            if s["key"] == key:
                s["status"] = status

                if detail:
                    s["detail"] = detail

                self._maybe_refresh()
                return

        self.steps.append(
            {"key": key, "label": key, "status": status, "detail": detail})
        self._maybe_refresh()

    def _maybe_refresh(self):

        if self._refresh_cb:
            try:
                self._refresh_cb()
            except Exception:
                pass

    def render(self):
        tree = Tree(f"[cyan]{self.title}[/cyan]", guide_style="grey50")
        for step in self.steps:
            label = step["label"]
            detail_text = step["detail"].strip() if step["detail"] else ""

            status = step["status"]
            if status == "done":
                symbol = "[green]OK[/green]"

            elif status == "pending":
                symbol = "[green dim]..[/green dim]"

            elif status == "running":
                symbol = "[cyan]>>[/cyan]"

            elif status == "error":
                symbol = "[red]!![/red]"

            elif status == "skipped":
                symbol = "[yellow]--[/yellow]"

            else:
                symbol = " "

            if status == "pending":
                # Entire line light gray (pending)

                if detail_text:
                    line = f"{symbol} [bright_black]{label} ({detail_text})[/bright_black]"

                else:
                    line = f"{symbol} [bright_black]{label}[/bright_black]"

            else:
                # Label white, detail (if any) light gray in parentheses
                if detail_text:
                    line = f"{symbol} [white]{label}[/white] [bright_black]({detail_text})[/bright_black]"

                else:
                    line = f"{symbol} [white]{label}[/white]"

            tree.add(line)

        return tree


def get_key():
    """Get a single keypress in a cross-platform way using readchar."""
    key = readchar.readkey()
    if key == readchar.key.UP or key == readchar.key.CTRL_P:
        return 'up'

    if key == readchar.key.DOWN or key == readchar.key.CTRL_N:
        return 'down'

    if key == readchar.key.ENTER:
        return 'enter'

    if key == readchar.key.ESC:
        return 'escape'

    if key == readchar.key.CTRL_C:
        raise KeyboardInterrupt

    return key


def select_with_arrows(options: dict, prompt_text: str = "Select an option", default_key: str = None) -> str:
    """
    Interactive selection using arrow keys with Rich Live display.


    Args:
        options: Dict with keys as option keys and values as descriptions
        prompt_text: Text to show above the options
        default_key: Default option key to start with

    Returns:
        Selected option key
    """
    option_keys = list(options.keys())
    if default_key and default_key in option_keys:
        selected_index = option_keys.index(default_key)

    else:
        selected_index = 0

    selected_key = None

    def create_selection_panel():
        """Create the selection panel with current selection highlighted."""
        table = Table.grid(padding=(0, 2))
        table.add_column(style="cyan", justify="left", width=3)
        table.add_column(style="white", justify="left")
        for i, key in enumerate(option_keys):
            if i == selected_index:
                table.add_row(
                    "->", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

            else:
                table.add_row(
                    " ", f"[cyan]{key}[/cyan] [dim]({options[key]})[/dim]")

        table.add_row("", "")
        table.add_row(
            "", "[dim]Use Up/Down arrows to navigate, Enter to select, Esc to cancel[/dim]")

        return Panel(
            table,
            title=f"[bold]{prompt_text}[/bold]",
            border_style="cyan",
            padding=(1, 2)
        )

    console.print()

    def run_selection_loop():
        nonlocal selected_key, selected_index
        with Live(create_selection_panel(), console=console, transient=True, auto_refresh=False) as live:
            while True:
                try:
                    key = get_key()
                    if key == 'up':
                        selected_index = (
                            selected_index - 1) % len(option_keys)

                    elif key == 'down':
                        selected_index = (
                            selected_index + 1) % len(option_keys)

                    elif key == 'enter':
                        selected_key = option_keys[selected_index]
                        break

                    elif key == 'escape':
                        console.print("\n[yellow]Selection cancelled[/yellow]")
                        raise typer.Exit(1)

                    live.update(create_selection_panel(), refresh=True)

                except KeyboardInterrupt:
                    console.print("\n[yellow]Selection cancelled[/yellow]")
                    raise typer.Exit(1)

    run_selection_loop()

    if selected_key is None:
        console.print("\n[red]Selection failed.[/red]")
        raise typer.Exit(1)

    return selected_key


console = Console()


class BannerGroup(TyperGroup):
    """Custom group that shows banner before help."""

    def format_help(self, ctx, formatter):
        # Show banner before help
        show_banner()
        super().format_help(ctx, formatter)


app = typer.Typer(
    name="specify",
    help="Setup tool for Specify spec-driven development projects",
    add_completion=False,
    invoke_without_command=True,
    cls=BannerGroup,
)


def show_banner():
    """Display the ASCII art banner."""
    banner_lines = BANNER.strip().split('\n')
    colors = ["bright_blue", "blue", "cyan",
              "bright_cyan", "white", "bright_white"]
    styled_banner = Text()

    for i, line in enumerate(banner_lines):
        color = colors[i % len(colors)]
        styled_banner.append(line + "\n", style=color)

    console.print(Align.center(styled_banner))
    console.print(Align.center(Text(TAGLINE, style="italic bright_yellow")))
    console.print()


@app.callback()
def callback(ctx: typer.Context):
    """Show banner when no subcommand is provided."""

    if ctx.invoked_subcommand is None and "--help" not in sys.argv and "-h" not in sys.argv:

        show_banner()

        console.print(Align.center(
            "[dim]Run 'specify --help' for usage information[/dim]"))

        console.print()


def run_command(cmd: list[str], check_return: bool = True, capture: bool = False, shell: bool = False) -> Optional[str]:
    """Run a shell command and optionally capture output."""

    try:

        if capture:

            result = subprocess.run(
                cmd, check=check_return, capture_output=True, text=True, shell=shell)

            return result.stdout.strip()

        else:

            subprocess.run(cmd, check=check_return, shell=shell)

            return None

    except subprocess.CalledProcessError as e:

        if check_return:

            console.print(f"[red]Error running command:[/red] {' '.join(cmd)}")

            console.print(f"[red]Exit code:[/red] {e.returncode}")

            if hasattr(e, 'stderr') and e.stderr:

                console.print(f"[red]Error output:[/red] {e.stderr}")

            raise

        return None


def check_tool(tool: str, tracker: StepTracker = None) -> bool:
    """Check if a tool is installed. Optionally update tracker.



    Args:

        tool: Name of the tool to check

        tracker: Optional StepTracker to update with results



    Returns:

        True if tool is found, False otherwise

    """

    # Special handling for Claude CLI after `claude migrate-installer`

    # See: https://github.com/github/spec-kit/issues/123

    # The migrate-installer command REMOVES the original executable from PATH

    # and creates an alias at ~/.claude/local/claude instead

    # This path should be prioritized over other claude executables in PATH

    if tool == "claude":

        if CLAUDE_LOCAL_PATH.exists() and CLAUDE_LOCAL_PATH.is_file():

            if tracker:

                tracker.complete(tool, "available")

            return True

    found = shutil.which(tool) is not None

    if tracker:

        if found:

            tracker.complete(tool, "available")

        else:

            tracker.error(tool, "not found")

    return found


def handle_vscode_settings(sub_item, dest_file, rel_path, verbose=False, tracker=None) -> None:
    """Handle merging or copying of .vscode/settings.json files."""

    def log(message, color="green"):

        if verbose and not tracker:

            console.print(f"[{color}]{message}[/] {rel_path}")

    try:

        with open(sub_item, 'r', encoding='utf-8') as f:

            new_settings = json.load(f)

        if dest_file.exists():

            merged = merge_json_files(
                dest_file, new_settings, verbose=verbose and not tracker)

            with open(dest_file, 'w', encoding='utf-8') as f:

                json.dump(merged, f, indent=4)

                f.write('\n')

            log("Merged:", "green")

        else:

            shutil.copy2(sub_item, dest_file)

            log("Copied (no existing settings.json):", "blue")

    except Exception as e:

        log(f"Warning: Could not merge, copying instead: {e}", "yellow")

        shutil.copy2(sub_item, dest_file)


def merge_json_files(existing_path: Path, new_content: dict, verbose: bool = False) -> dict:
    """Merge new JSON content into existing JSON file.



    Performs a deep merge where:

    - New keys are added

    - Existing keys are preserved unless overwritten by new content

    - Nested dictionaries are merged recursively

    - Lists and other values are replaced (not merged)



    Args:

        existing_path: Path to existing JSON file

        new_content: New JSON content to merge in

        verbose: Whether to print merge details



    Returns:

        Merged JSON content as dict

    """

    try:

        with open(existing_path, 'r', encoding='utf-8') as f:

            existing_content = json.load(f)

    except (FileNotFoundError, json.JSONDecodeError):

        # If file doesn't exist or is invalid, just use new content

        return new_content

    def deep_merge(base: dict, update: dict) -> dict:
        """Recursively merge update dict into base dict."""

        result = base.copy()

        for key, value in update.items():

            if key in result and isinstance(result[key], dict) and isinstance(value, dict):

                # Recursively merge nested dictionaries

                result[key] = deep_merge(result[key], value)

            else:

                # Add new key or replace existing value

                result[key] = value

        return result

    merged = deep_merge(existing_content, new_content)

    if verbose:

        console.print(f"[cyan]Merged JSON file:[/cyan] {existing_path.name}")

    return merged

    if verbose:

        console.print("[cyan]Fetching latest release information...[/cyan]")

    api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"

    try:

        response = client.get(

            api_url,

            timeout=30,

            follow_redirects=True,

            headers=_github_auth_headers(github_token),

        )

        status = response.status_code

        if status != 200:

            msg = f"GitHub API returned {status} for {api_url}"

            if debug:

                msg += f"\nResponse headers: {response.headers}\nBody (truncated 500): {response.text[:500]}"

            raise RuntimeError(msg)

        try:

            release_data = response.json()

        except ValueError as je:

            raise RuntimeError(
                f"Failed to parse release JSON: {je}\nRaw (truncated 400): {response.text[:400]}")

    except Exception as e:

        console.print(f"[red]Error fetching release information[/red]")

        console.print(Panel(str(e), title="Fetch Error", border_style="red"))

        raise typer.Exit(1)

    assets = release_data.get("assets", [])

    pattern = f"spec-kit-template-{ai_assistant}-{script_type}"

    matching_assets = [

        asset for asset in assets

        if pattern in asset["name"] and asset["name"].endswith(".zip")

    ]

    asset = matching_assets[0] if matching_assets else None

    if asset is None:

        console.print(
            f"[red]No matching release asset found[/red] for [bold]{ai_assistant}[/bold] (expected pattern: [bold]{pattern}[/bold])")

        asset_names = [a.get('name', '?') for a in assets]

        console.print(Panel("\n".join(asset_names) or "(no assets)",
                      title="Available Assets", border_style="yellow"))

        raise typer.Exit(1)

    download_url = asset["browser_download_url"]

    filename = asset["name"]

    file_size = asset["size"]

    if verbose:

        console.print(f"[cyan]Found template:[/cyan] {filename}")

        console.print(f"[cyan]Size:[/cyan] {file_size:,} bytes")

        console.print(f"[cyan]Release:[/cyan] {release_data['tag_name']}")

    zip_path = download_dir / filename

    if verbose:

        console.print(f"[cyan]Downloading template...[/cyan]")

    try:

        with client.stream(

            "GET",

            download_url,

            timeout=60,

            follow_redirects=True,

            headers=_github_auth_headers(github_token),

        ) as response:

            if response.status_code != 200:

                body_sample = response.text[:400]

                raise RuntimeError(
                    f"Download failed with {response.status_code}\nHeaders: {response.headers}\nBody (truncated): {body_sample}")

            total_size = int(response.headers.get('content-length', 0))

            with open(zip_path, 'wb') as f:

                if total_size == 0:

                    for chunk in response.iter_bytes(chunk_size=8192):

                        f.write(chunk)

                else:

                    if show_progress:

                        with Progress(

                            SpinnerColumn(),

                            TextColumn(
                                "[progress.description]{task.description}"),

                            TextColumn(
                                "[progress.percentage]{task.percentage:>3.0f}%"),

                            console=console,

                        ) as progress:

                            task = progress.add_task(
                                "Downloading...", total=total_size)

                            downloaded = 0

                            for chunk in response.iter_bytes(chunk_size=8192):

                                f.write(chunk)

                                downloaded += len(chunk)

                                progress.update(task, completed=downloaded)

                    else:

                        for chunk in response.iter_bytes(chunk_size=8192):

                            f.write(chunk)

    except Exception as e:

        console.print(f"[red]Error downloading template[/red]")

        detail = str(e)

        if zip_path.exists():

            zip_path.unlink()

        console.print(
            Panel(detail, title="Download Error", border_style="red"))

        raise typer.Exit(1)

    if verbose:

        console.print(f"Downloaded: {filename}")

    metadata = {

        "filename": filename,

        "size": file_size,

        "release": release_data["tag_name"],

        "asset_url": download_url

    }

    return zip_path, metadata

    if tracker:

        tracker.start("fetch", "contacting GitHub API")

    try:

        zip_path, meta = download_template_from_github(

            ai_assistant,

            current_dir,

            script_type=script_type,

            verbose=verbose and tracker is None,

            show_progress=(tracker is None),

            client=client,

            debug=debug,

            github_token=github_token

        )

        if tracker:

            tracker.complete(
                "fetch", f"release {meta['release']} ({meta['size']:,} bytes)")

            tracker.add("download", "Download template")

            tracker.complete("download", meta['filename'])

    except Exception as e:

        if tracker:

            tracker.error("fetch", str(e))

        else:

            if verbose:

                console.print(f"[red]Error downloading template:[/red] {e}")

        raise

    if tracker:

        tracker.add("extract", "Extract template")

        tracker.start("extract")

    elif verbose:

        console.print("Extracting template...")

    try:

        if not is_current_dir:

            project_path.mkdir(parents=True)

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            zip_contents = zip_ref.namelist()

            if tracker:

                tracker.start("zip-list")

                tracker.complete("zip-list", f"{len(zip_contents)} entries")

            elif verbose:

                console.print(
                    f"[cyan]ZIP contains {len(zip_contents)} items[/cyan]")

            if is_current_dir:

                with tempfile.TemporaryDirectory() as temp_dir:

                    temp_path = Path(temp_dir)

                    zip_ref.extractall(temp_path)

                    extracted_items = list(temp_path.iterdir())

                    if tracker:

                        tracker.start("extracted-summary")

                        tracker.complete("extracted-summary",
                                         f"temp {len(extracted_items)} items")

                    elif verbose:

                        console.print(
                            f"[cyan]Extracted {len(extracted_items)} items to temp location[/cyan]")

                    source_dir = temp_path

                    if len(extracted_items) == 1 and extracted_items[0].is_dir():

                        source_dir = extracted_items[0]

                        if tracker:

                            tracker.add("flatten", "Flatten nested directory")

                            tracker.complete("flatten")

                        elif verbose:

                            console.print(
                                f"[cyan]Found nested directory structure[/cyan]")

                    for item in source_dir.iterdir():

                        dest_path = project_path / item.name

                        if item.is_dir():

                            if dest_path.exists():

                                if verbose and not tracker:

                                    console.print(
                                        f"[yellow]Merging directory:[/yellow] {item.name}")

                                for sub_item in item.rglob('*'):

                                    if sub_item.is_file():

                                        rel_path = sub_item.relative_to(item)

                                        dest_file = dest_path / rel_path

                                        dest_file.parent.mkdir(
                                            parents=True, exist_ok=True)

                                        # Special handling for .vscode/settings.json - merge instead of overwrite

                                        if dest_file.name == "settings.json" and dest_file.parent.name == ".vscode":

                                            handle_vscode_settings(
                                                sub_item, dest_file, rel_path, verbose, tracker)

                                        else:

                                            shutil.copy2(sub_item, dest_file)

                            else:

                                shutil.copytree(item, dest_path)

                        else:

                            if dest_path.exists() and verbose and not tracker:

                                console.print(
                                    f"[yellow]Overwriting file:[/yellow] {item.name}")

                            shutil.copy2(item, dest_path)

                    if verbose and not tracker:

                        console.print(
                            f"[cyan]Template files merged into current directory[/cyan]")

            else:

                zip_ref.extractall(project_path)

                extracted_items = list(project_path.iterdir())

                if tracker:

                    tracker.start("extracted-summary")

                    tracker.complete("extracted-summary",
                                     f"{len(extracted_items)} top-level items")

                elif verbose:

                    console.print(
                        f"[cyan]Extracted {len(extracted_items)} items to {project_path}:[/cyan]")

                    for item in extracted_items:

                        console.print(
                            f"  - {item.name} ({'dir' if item.is_dir() else 'file'})")

                if len(extracted_items) == 1 and extracted_items[0].is_dir():

                    nested_dir = extracted_items[0]

                    temp_move_dir = project_path.parent / \
                        f"{project_path.name}_temp"

                    shutil.move(str(nested_dir), str(temp_move_dir))

                    project_path.rmdir()

                    shutil.move(str(temp_move_dir), str(project_path))

                    if tracker:

                        tracker.add("flatten", "Flatten nested directory")

                        tracker.complete("flatten")

                    elif verbose:

                        console.print(
                            f"[cyan]Flattened nested directory structure[/cyan]")

    except Exception as e:

        if tracker:

            tracker.error("extract", str(e))

        else:

            if verbose:

                console.print(f"[red]Error extracting template:[/red] {e}")

                if debug:

                    console.print(
                        Panel(str(e), title="Extraction Error", border_style="red"))

        if not is_current_dir and project_path.exists():

            shutil.rmtree(project_path)

        raise typer.Exit(1)

    else:

        if tracker:

            tracker.complete("extract")

    finally:

        if tracker:

            tracker.add("cleanup", "Remove temporary archive")

        if zip_path.exists():

            zip_path.unlink()

            if tracker:

                tracker.complete("cleanup")

            elif verbose:

                console.print(f"Cleaned up: {zip_path.name}")

    return project_path


def ensure_executable_scripts(project_path: Path, tracker: StepTracker | None = None) -> None:
    """Ensure POSIX .sh scripts under .specify/scripts (recursively) have execute bits (no-op on Windows)."""

    if os.name == "nt":

        return  # Windows: skip silently

    scripts_root = project_path / ".specify" / "scripts"

    if not scripts_root.is_dir():

        return

    failures: list[str] = []

    updated = 0

    for script in scripts_root.rglob("*.sh"):

        try:

            if script.is_symlink() or not script.is_file():

                continue

            try:

                with script.open("rb") as f:

                    if f.read(2) != b"#!":

                        continue

            except Exception:

                continue

            st = script.stat()
            mode = st.st_mode

            if mode & 0o111:

                continue

            new_mode = mode

            if mode & 0o400:
                new_mode |= 0o100

            if mode & 0o040:
                new_mode |= 0o010

            if mode & 0o004:
                new_mode |= 0o001

            if not (new_mode & 0o100):

                new_mode |= 0o100

            os.chmod(script, new_mode)

            updated += 1

        except Exception as e:

            failures.append(f"{script.relative_to(scripts_root)}: {e}")

    if tracker:

        detail = f"{updated} updated" + \
            (f", {len(failures)} failed" if failures else "")

        tracker.add("chmod", "Set script permissions recursively")

        (tracker.error if failures else tracker.complete)("chmod", detail)

    else:

        if updated:

            console.print(
                f"[cyan]Updated execute permissions on {updated} script(s) recursively[/cyan]")

        if failures:

            console.print(
                "[yellow]Some scripts could not be updated:[/yellow]")

            for f in failures:

                console.print(f"  - {f}")


@app.command()
def init(

    target: str = typer.Argument(
        '.', help="Existing workspace directory (use '.' for current directory)"),

    ai_assistant: str = typer.Option(
        None, '--ai', help="AI assistant to use: claude, gemini, copilot, cursor-agent, qwen, opencode, codex, windsurf, kilocode, auggie, codebuddy, amp, roo, or q"),

    script_type: str = typer.Option(
        None, '--script', help="Script type to use: sh or ps"),

    ignore_agent_tools: bool = typer.Option(
        False, '--ignore-agent-tools', help="Skip checks for AI agent tools like Claude Code"),

    force: bool = typer.Option(
        False, '--force', help="Overwrite existing Specify assets without confirmation"),

    debug: bool = typer.Option(
        False, '--debug', help="Show verbose diagnostic output for troubleshooting"),

):
    '''Prepare Spec Kit assets within an existing workspace.



    This command will:

    1. Let you choose your AI assistant

    2. Copy templates, memory, and scripts into the workspace

    3. Generate agent-specific commands locally

    4. Ensure architecture scaffolding is available under specs/

    '''

    show_banner()

    project_path = Path(target).resolve()

    if not project_path.exists():

        error_panel = Panel(

            f"Directory '[cyan]{project_path}[/cyan]' does not exist",

            title='[red]Invalid Path[/red]',

            border_style='red',

            padding=(1, 2),

        )

        console.print()

        console.print(error_panel)

        raise typer.Exit(1)

    if not project_path.is_dir():

        error_panel = Panel(

            f"Path '[cyan]{project_path}[/cyan]' is not a directory",

            title='[red]Invalid Path[/red]',

            border_style='red',

            padding=(1, 2),

        )

        console.print()

        console.print(error_panel)

        raise typer.Exit(1)

    specify_dir = project_path / '.specify'

    agent_folder = None

    if ai_assistant and ai_assistant in AGENT_CONFIG:

        agent_folder = AGENT_CONFIG[ai_assistant]['folder']

    if specify_dir.exists() and not force:

        warning_panel = Panel(

            "Existing .specify content detected. Continuing may overwrite files.",

            title='[yellow]Existing Specify Assets[/yellow]',

            border_style='yellow',

            padding=(1, 2),

        )

        console.print()

        console.print(warning_panel)

        if not typer.confirm('Do you want to continue and merge the new assets?'):

            console.print('[yellow]Operation cancelled[/yellow]')

            raise typer.Exit(0)

    working_dir = Path.cwd()

    setup_lines = [

        '[cyan]Specify Workspace Setup[/cyan]',

        '',

        f"{'Target Path':<15} [green]{project_path}[/green]",

        f"{'Working Path':<15} [dim]{working_dir}[/dim]",

    ]

    console.print(Panel('\n'.join(setup_lines),
                  border_style='cyan', padding=(1, 2)))

    if ai_assistant:

        if ai_assistant not in AGENT_CONFIG:

            console.print(
                f"[red]Error:[/red] Invalid AI assistant '{ai_assistant}'. Choose from: {', '.join(AGENT_CONFIG.keys())}")

            raise typer.Exit(1)

        selected_ai = ai_assistant

    else:

        ai_choices = {key: config['name']
                      for key, config in AGENT_CONFIG.items()}

        selected_ai = select_with_arrows(

            ai_choices,

            'Choose your AI assistant:',

            'copilot'

        )

    agent_folder = AGENT_CONFIG[selected_ai]['folder']

    if not ignore_agent_tools:

        agent_config = AGENT_CONFIG.get(selected_ai)

        if agent_config and agent_config['requires_cli']:

            install_url = agent_config['install_url']

            if not check_tool(selected_ai):

                error_panel = Panel(

                    f"[cyan]{selected_ai}[/cyan] not found\n"

                    f"Install from: [cyan]{install_url}[/cyan]\n"

                    f"{agent_config['name']} is required to continue with this project type.\n\n"

                    "Tip: Use [cyan]--ignore-agent-tools[/cyan] to skip this check",

                    title='[red]Agent Detection Error[/red]',

                    border_style='red',

                    padding=(1, 2),

                )

                console.print()

                console.print(error_panel)

                raise typer.Exit(1)

    if script_type:

        if script_type not in SCRIPT_TYPE_CHOICES:

            console.print(
                f"[red]Error:[/red] Invalid script type '{script_type}'. Choose from: {', '.join(SCRIPT_TYPE_CHOICES.keys())}")

            raise typer.Exit(1)

        selected_script = script_type

    else:

        default_script = 'ps' if os.name == 'nt' else 'sh'

        if sys.stdin.isatty():

            selected_script = select_with_arrows(
                SCRIPT_TYPE_CHOICES, 'Choose script type (or press Enter)', default_script)

        else:

            selected_script = default_script

    console.print(f"[cyan]Selected AI assistant:[/cyan] {selected_ai}")

    console.print(f"[cyan]Selected script type:[/cyan] {selected_script}")

    tracker = StepTracker('Prepare Specify Workspace')

    sys._specify_tracker_active = True  # type: ignore[attr-defined]

    for key, label in [

        ('prepare', 'Prepare workspace directories'),

        ('copy-memory', 'Copy memory resources'),

        ('copy-scripts', 'Copy helper scripts'),

        ('copy-templates', 'Copy templates'),

        ('commands', 'Generate AI commands'),

        ('architecture', 'Seed architecture commands'),

        ('chmod', 'Ensure scripts executable'),

        ('final', 'Finalize'),

    ]:

        tracker.add(key, label)

    with Live(tracker.render(), console=console, refresh_per_second=8, transient=True) as live:

        tracker.attach_refresh(lambda: live.update(tracker.render()))

        try:

            prepare_workspace(project_path, selected_ai,
                              selected_script, force=force, tracker=tracker)

            tracker.start('chmod')

            ensure_executable_scripts(project_path, tracker=tracker)

            tracker.complete('final', 'workspace ready')

        except Exception as e:

            tracker.error('final', str(e))

            console.print(
                Panel(f'Initialization failed: {e}', title='Failure', border_style='red'))

            if debug:

                _env_pairs = [

                    ('Python', sys.version.split()[0]),

                    ('Platform', sys.platform),

                    ('CWD', str(Path.cwd())),

                ]

                _label_width = max(len(k) for k, _ in _env_pairs)

                env_lines = [
                    f"{k.ljust(_label_width)} -> [bright_black]{v}[/bright_black]" for k, v in _env_pairs]

                console.print(
                    Panel('\n'.join(env_lines), title='Debug Environment', border_style='magenta'))

            raise typer.Exit(1)

    console.print(tracker.render())

    console.print('\n[bold green]Workspace ready.[/bold green]')

    agent_config = AGENT_CONFIG.get(selected_ai)

    if agent_config:

        agent_folder = agent_config['folder']

        security_notice = Panel(

            f'Some agents may store credentials, auth tokens, or other identifying and private artifacts in the agent folder within your project.\n'

            f'Consider adding [cyan]{agent_folder}[/cyan] (or parts of it) to [cyan].gitignore[/cyan] to prevent accidental credential leakage.',

            title='[yellow]Agent Folder Security[/yellow]',

            border_style='yellow',

            padding=(1, 2),

        )

        console.print()

        console.print(security_notice)

    steps_lines: list[str] = []

    if project_path == working_dir:

        steps_lines.append("1. You're already in the workspace root!")

        step_num = 2

    else:

        steps_lines.append(
            f"1. Go to the workspace folder: [cyan]cd {project_path}[/cyan]")

        step_num = 2

    if selected_ai == 'codex':

        codex_prompts_src = project_path / '.codex' / 'prompts'
        codex_prompts_dst = Path.home() / '.codex' / 'prompts'

        steps_lines.append(
            f"{step_num}. Copy Codex prompts into your home profile: [cyan]{codex_prompts_src} -> {codex_prompts_dst}[/cyan]")
        steps_lines.append(
            '   [bright_black](Current Codex releases ignore prompts stored inside the workspace; place them under ~/.codex/prompts.)[/bright_black]')

        step_num += 1

    steps_lines.append(
        f"{step_num}. Start using slash commands with your AI agent:")

    command_prefix = step_num

    steps_lines.append(
        f'   {command_prefix}.1 [cyan]/specify.constitution[/] - Establish project principles')

    steps_lines.append(
        f'   {command_prefix}.2 [cyan]/specify.architecture.create[/] - Analyse the repository and create the full architecture model')

    steps_lines.append(
        f'   {command_prefix}.3 [cyan]/specify.specify[/] - Create baseline specification')

    steps_lines.append(
        f'   {command_prefix}.4 [cyan]/specify.plan[/] - Create implementation plan')

    steps_lines.append(
        f'   {command_prefix}.5 [cyan]/specify.tasks[/] - Generate actionable tasks')

    steps_lines.append(
        f'   {command_prefix}.6 [cyan]/specify.implement[/] - Execute implementation')

    steps_panel = Panel('\n'.join(steps_lines),
                        title='Next Steps', border_style='cyan', padding=(1, 2))

    console.print()

    console.print(steps_panel)

    enhancement_lines = [

        'Optional commands that you can use for your specs [bright_black](improve quality & confidence)[/bright_black]',

        '',

        "- [cyan]/specify.clarify[/] [bright_black](optional)[/bright_black] - Ask structured questions to de-risk ambiguous areas before planning (run before [cyan]/specify.plan[/] if used)",

        "- [cyan]/specify.analyze[/] [bright_black](optional)[/bright_black] - Cross-artifact consistency & alignment report (after [cyan]/specify.tasks[/], before [cyan]/specify.implement[/])",

        "- [cyan]/specify.checklist[/] [bright_black](optional)[/bright_black] - Generate quality checklists to validate requirements completeness, clarity, and consistency (after [cyan]/specify.plan[/])",

    ]

    enhancements_panel = Panel('\n'.join(
        enhancement_lines), title='Enhancement Commands', border_style='cyan', padding=(1, 2))

    console.print()

    console.print(enhancements_panel)


@app.command()
def check():
    """Check that all required tools are installed."""

    show_banner()

    console.print("[bold]Checking for installed tools...[/bold]\n")

    tracker = StepTracker("Check Available Tools")

    agent_results = {}

    for agent_key, agent_config in AGENT_CONFIG.items():

        agent_name = agent_config["name"]

        requires_cli = agent_config["requires_cli"]

        tracker.add(agent_key, agent_name)

        if requires_cli:

            agent_results[agent_key] = check_tool(agent_key, tracker=tracker)

        else:

            # IDE-based agent - skip CLI check and mark as optional

            tracker.skip(agent_key, "IDE-based, no CLI check")

            # Don't count IDE agents as "found"
            agent_results[agent_key] = False

    # Check VS Code variants (not in agent config)

    tracker.add("code", "Visual Studio Code")

    code_ok = check_tool("code", tracker=tracker)

    tracker.add("code-insiders", "Visual Studio Code Insiders")

    code_insiders_ok = check_tool("code-insiders", tracker=tracker)

    console.print(tracker.render())

    console.print("\n[bold green]Specify CLI is ready to use![/bold green]")

    if not any(agent_results.values()):

        console.print(
            "[dim]Tip: Install an AI assistant for the best experience[/dim]")


def ensure_architecture_templates(project_path: Path) -> None:
    """Guarantee architecture template files exist under .specify/templates."""

    templates_src = _asset_path("templates")

    templates_dst = project_path / ".specify" / "templates"

    templates_dst.mkdir(parents=True, exist_ok=True)

    for filename in ARCHITECTURE_TEMPLATE_FILES:

        src_path = templates_src / filename

        if not src_path.exists():

            continue

        dst_path = templates_dst / filename

        if not dst_path.exists():

            shutil.copy2(src_path, dst_path)


def ensure_architecture_scripts(project_path: Path) -> None:
    """Ensure architecture helper scripts are available for both shells."""

    scripts_src = _asset_path("scripts")

    scripts_dst = project_path / ".specify" / "scripts"

    scripts_dst.mkdir(parents=True, exist_ok=True)

    for shell_name in ("bash", "powershell"):

        src_dir = scripts_src / shell_name

        if not src_dir.is_dir():

            continue

        dst_dir = scripts_dst / shell_name

        dst_dir.mkdir(parents=True, exist_ok=True)

        for script in src_dir.glob("architecture-info.*"):

            dst_path = dst_dir / script.name

            if not dst_path.exists():

                shutil.copy2(script, dst_path)

                if os.name != "nt" and script.suffix == ".sh":

                    os.chmod(dst_path, 0o755)


def ensure_agent_commands(project_path: Path, agent_key: str, script_type: str, tracker: StepTracker | None = None) -> None:

    agent_cfg = AGENT_OUTPUT_CONFIG.get(agent_key)

    agent_folder = AGENT_CONFIG.get(agent_key, {}).get("folder")

    if not agent_cfg or not agent_folder:

        if tracker:

            tracker.skip("commands", "Unsupported agent configuration")

        return

    templates_dir = _asset_path("templates", "commands")

    target_dir = project_path / agent_folder / agent_cfg["subdir"]

    target_dir.mkdir(parents=True, exist_ok=True)

    count = 0

    for template_path in sorted(templates_dir.glob("*.md")):

        name = template_path.stem

        if name.startswith("architecture."):

            continue

        template_body = template_path.read_text(encoding="utf-8")

        rendered = render_agent_command(

            template=template_body,

            agent_key=agent_key,

            script_type=script_type,

            args_token=agent_cfg["args_token"],

            extension=agent_cfg["extension"],

        )

        output_name = f"specify.{name}.{agent_cfg['extension']}"

        (target_dir / output_name).write_text(rendered, encoding="utf-8")

        count += 1

    if agent_key == "copilot":

        try:

            settings_src = _asset_path("templates", "vscode-settings.json")

        except FileNotFoundError:

            settings_src = None

        if settings_src and settings_src.exists():

            vscode_dir = project_path / ".vscode"

            vscode_dir.mkdir(parents=True, exist_ok=True)

            shutil.copy2(settings_src, vscode_dir / "settings.json")

    if tracker:

        tracker.complete("commands", f"{count} command file(s)")


def _rewrite_command_paths(text: str) -> str:

    for old, new in (("memory/", ".specify/memory/"), ("scripts/", ".specify/scripts/"), ("templates/", ".specify/templates/")):

        text = text.replace(old, new)

    return text


def _parse_command_template(template: str) -> tuple[str, dict[str, str], dict[str, str], str]:

    if not template.startswith("---"):

        return "", {}, {}, template

    parts = template.split("---", 2)

    if len(parts) < 3:

        return "", {}, {}, template

    front_matter_lines = parts[1].splitlines()

    body = parts[2]

    description = ""

    scripts: dict[str, str] = {}

    agent_scripts: dict[str, str] = {}

    current = None

    for line in front_matter_lines:

        if line.startswith("description:"):

            description = line.split(":", 1)[1].strip()

        elif line.strip() == "scripts:":

            current = "scripts"

        elif line.strip() == "agent_scripts:":

            current = "agent_scripts"

        elif line.startswith("  ") and current:

            key, value = line.strip().split(":", 1)

            value = value.strip()

            if current == "scripts":

                scripts[key.strip()] = value

            else:

                agent_scripts[key.strip()] = value

        else:

            current = None

    return description, scripts, agent_scripts, body


AGENT_OUTPUT_CONFIG = {

    "claude": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "gemini": {"subdir": "commands", "extension": "toml", "args_token": "{{args}}"},

    "copilot": {"subdir": "prompts", "extension": "prompt.md", "args_token": "$ARGUMENTS"},

    "cursor-agent": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "qwen": {"subdir": "commands", "extension": "toml", "args_token": "{{args}}"},

    "opencode": {"subdir": "command", "extension": "md", "args_token": "$ARGUMENTS"},

    "codex": {"subdir": "prompts", "extension": "md", "args_token": "$ARGUMENTS"},

    "windsurf": {"subdir": "workflows", "extension": "md", "args_token": "$ARGUMENTS"},

    "kilocode": {"subdir": "workflows", "extension": "md", "args_token": "$ARGUMENTS"},

    "auggie": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "roo": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "codebuddy": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "amp": {"subdir": "commands", "extension": "md", "args_token": "$ARGUMENTS"},

    "q": {"subdir": "prompts", "extension": "md", "args_token": "$ARGUMENTS"},

}


def render_agent_command(template: str, agent_key: str, script_type: str, args_token: str, extension: str) -> str:

    description, scripts, agent_scripts, body = _parse_command_template(
        template)

    script_command = scripts.get(script_type) or scripts.get("sh") or ""

    agent_script_command = agent_scripts.get(script_type) or ""

    body = body.replace("{SCRIPT}", script_command)

    body = body.replace("{AGENT_SCRIPT}", agent_script_command)

    body = body.replace("{ARGS}", args_token)

    body = body.replace("__AGENT__", agent_key)

    body = _rewrite_command_paths(body)

    if extension == "toml":

        escaped_body = body.replace("\\", "\\\\")

        return f'description = "{description}"\n\nprompt = """\n{escaped_body}\n"""\n'

    else:

        header = f"---\ndescription: {description}\n---\n\n" if description else ""

        return header + body.strip() + "\n"


def ensure_architecture_commands(project_path: Path, agent_key: str, script_type: str, tracker: StepTracker | None = None) -> None:

    agent_cfg = AGENT_OUTPUT_CONFIG.get(agent_key)

    agent_folder = AGENT_CONFIG.get(agent_key, {}).get("folder")

    if not agent_cfg or not agent_folder:

        if tracker:

            tracker.skip("architecture", "Unsupported agent configuration")

        return

    templates_dir = _asset_path("templates", "commands")

    target_dir = project_path / agent_folder / agent_cfg["subdir"]

    target_dir.mkdir(parents=True, exist_ok=True)

    legacy_bases = [

        "specify.create",

        "specify.update",

        "specify.architecture-create",

        "specify.architecture-update",

    ]

    for legacy in legacy_bases:

        legacy_path = target_dir / f"{legacy}.{agent_cfg['extension']}"

        if legacy_path.exists():

            legacy_path.unlink()

    count = 0

    for template_path in sorted(templates_dir.glob("architecture.*.md")):

        template_body = template_path.read_text(encoding="utf-8")

        name = template_path.stem  # e.g. architecture.create

        filename = f"specify.{name}.{agent_cfg['extension']}"

        target_path = target_dir / filename

        if target_path.exists():

            continue

        rendered = render_agent_command(

            template=template_body,

            agent_key=agent_key,

            script_type=script_type,

            args_token=agent_cfg["args_token"],

            extension=agent_cfg["extension"],

        )

        target_path.write_text(rendered, encoding="utf-8")

        count += 1

    if tracker:

        tracker.complete("architecture", f"{count} command file(s)")


def create_architecture_scaffold(project_path: Path) -> None:
    """Create specs/architecture scaffolding with placeholder artefacts."""

    architecture_dir = project_path / "specs" / "architecture"

    architecture_dir.mkdir(parents=True, exist_ok=True)

    readme_path = architecture_dir / "README.md"

    if not readme_path.exists():

        readme_path.write_text(
            ARCHITECTURE_DIRECTORY_OVERVIEW, encoding="utf-8")


def prepare_workspace(project_path: Path, agent_key: str, script_type: str, *, force: bool = False, tracker: StepTracker | None = None) -> None:
    '''Populate the workspace with Specify assets and agent-specific commands.'''

    specify_dir = project_path / '.specify'

    specs_dir = project_path / 'specs'

    if tracker:

        tracker.start('prepare')

    specify_dir.mkdir(parents=True, exist_ok=True)

    specs_dir.mkdir(parents=True, exist_ok=True)

    if tracker:

        tracker.complete('prepare', '.specify')

    if tracker:

        tracker.start('copy-memory')

    _sync_directory(_asset_path('memory'), specify_dir / 'memory')

    if tracker:

        tracker.complete('copy-memory', 'memory')

    if tracker:

        tracker.start('copy-scripts')

    _sync_directory(_asset_path('scripts'), specify_dir / 'scripts')

    if tracker:

        tracker.complete('copy-scripts', 'scripts')

    if tracker:

        tracker.start('copy-templates')

    _sync_directory(_asset_path('templates'), specify_dir / 'templates',
                    exclude_dirs={'commands'}, exclude_files={'vscode-settings.json'})

    if tracker:

        tracker.complete('copy-templates', 'templates')

    ensure_architecture_templates(project_path)

    ensure_architecture_scripts(project_path)

    create_architecture_scaffold(project_path)

    if tracker:

        tracker.start('commands')

    ensure_agent_commands(project_path, agent_key,
                          script_type, tracker=tracker)

    if tracker:

        tracker.start('architecture')

    ensure_architecture_commands(
        project_path, agent_key, script_type, tracker=tracker)


def main():
    app()


if __name__ == "__main__":
    main()
