"""
cli.py
======
Professional Typer-based CLI for Water Companion.

Commands
--------
  water-companion             → launch GUI (default)
  water-companion start       → launch GUI
  water-companion stop        → stop running instance
  water-companion pause       → pause reminders
  water-companion resume      → resume reminders
  water-companion status      → show current state
  water-companion config      → interactive interval picker
  water-companion reset       → reset to defaults
  water-companion version     → print version
"""

from __future__ import annotations

import json
import os
import signal
import socket
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from water_companion.utils.constants import (
    APP_NAME,
    APP_VERSION,
    IPC_PORT,
    PID_FILE,
    INTERVAL_OPTIONS,
)

# ─────────────────────────────────────────────────────────────────────────────
# Typer app
# ─────────────────────────────────────────────────────────────────────────────

app = typer.Typer(
    name="water-companion",
    help="💧 Water Companion — Your hydration reminder buddy.",
    add_completion=False,
    rich_markup_mode="rich",
)

console = Console()


# ─────────────────────────────────────────────────────────────────────────────
# IPC helpers  (simple TCP socket to running GUI instance)
# ─────────────────────────────────────────────────────────────────────────────

def _send_ipc(command: str) -> bool:
    """
    Send a one-line command to the running GUI instance over TCP.

    Returns True if the command was acknowledged, False otherwise.
    """
    try:
        with socket.create_connection(("127.0.0.1", IPC_PORT), timeout=2) as sock:
            sock.sendall((command + "\n").encode())
            response = sock.recv(256).decode().strip()
            return response == "OK"
    except (ConnectionRefusedError, OSError, TimeoutError):
        return False


def _is_running() -> bool:
    """Check whether a Water Companion GUI instance is accepting IPC connections."""
    return _send_ipc("ping")


# ─────────────────────────────────────────────────────────────────────────────
# Commands
# ─────────────────────────────────────────────────────────────────────────────

@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """💧 Water Companion — Your hydration reminder buddy."""
    if ctx.invoked_subcommand is None:
        # Default: launch the GUI
        _launch_gui()


@app.command()
def start() -> None:
    """Launch the Water Companion desktop application."""
    _launch_gui()


@app.command()
def stop() -> None:
    """Stop the running Water Companion instance."""
    if _send_ipc("quit"):
        console.print("[green]✓[/green] Water Companion stopped.")
    else:
        console.print("[yellow]⚠[/yellow] No running instance found.")


@app.command()
def pause() -> None:
    """Pause reminders without quitting."""
    if _send_ipc("pause"):
        console.print("[cyan]⏸[/cyan] Reminders paused.")
    else:
        console.print("[yellow]⚠[/yellow] No running instance found.")


@app.command()
def resume() -> None:
    """Resume paused reminders."""
    if _send_ipc("resume"):
        console.print("[green]▶[/green] Reminders resumed.")
    else:
        console.print("[yellow]⚠[/yellow] No running instance found.")


@app.command()
def status() -> None:
    """Show the current status of Water Companion."""
    # Try to get status from running instance
    try:
        with socket.create_connection(("127.0.0.1", IPC_PORT), timeout=2) as sock:
            sock.sendall(b"status\n")
            raw = sock.recv(1024).decode().strip()
            data = json.loads(raw)

            table = Table(box=box.ROUNDED, border_style="cyan", show_header=False)
            table.add_column("Key", style="bold cyan", width=20)
            table.add_column("Value", style="white")

            table.add_row("Status", f"[green]Running[/green]")
            table.add_row("State", data.get("state", "?"))
            table.add_row("Interval", f"{data.get('interval_minutes', '?')} minutes")
            remaining = int(data.get("remaining_seconds", 0))
            mins, secs = divmod(remaining, 60)
            table.add_row("Next reminder in", f"{mins}m {secs:02d}s")

            console.print(Panel(table, title=f"💧 {APP_NAME}", border_style="cyan"))
    except (ConnectionRefusedError, OSError, TimeoutError, json.JSONDecodeError):
        # Fall back to config file
        from water_companion.settings.config import load_config
        config = load_config()
        table = Table(box=box.ROUNDED, border_style="yellow", show_header=False)
        table.add_column("Key", style="bold yellow", width=20)
        table.add_column("Value", style="white")
        table.add_row("Status", "[yellow]Not running[/yellow]")
        table.add_row("Interval", f"{config.interval_minutes} minutes")
        table.add_row("Enabled", str(config.reminders_enabled))
        console.print(Panel(table, title=f"💧 {APP_NAME}", border_style="yellow"))


@app.command()
def config() -> None:
    """Interactively configure the reminder interval."""
    console.print(Panel("💧 [bold cyan]Water Companion — Configuration[/bold cyan]", border_style="cyan"))

    labels = list(INTERVAL_OPTIONS.keys())
    for i, label in enumerate(labels, start=1):
        console.print(f"  [cyan]{i}[/cyan].  {label}")

    console.print()
    choice_str = typer.prompt("Enter number")

    try:
        idx = int(choice_str) - 1
        if idx < 0 or idx >= len(labels):
            raise ValueError
        label = labels[idx]
        minutes = INTERVAL_OPTIONS[label]
    except (ValueError, IndexError):
        console.print("[red]Invalid choice.[/red]")
        raise typer.Exit(1)

    # Save to config
    from water_companion.settings.config import load_config, save_config
    cfg = load_config()
    cfg.interval_minutes = minutes
    save_config(cfg)

    console.print(f"[green]✓[/green] Interval set to [bold]{label}[/bold].")

    # Push to running instance if alive
    if _send_ipc(f"interval:{minutes}"):
        console.print("[green]✓[/green] Running instance updated.")


@app.command()
def reset() -> None:
    """Reset all settings to defaults."""
    confirm = typer.confirm("Reset all Water Companion settings to defaults?")
    if not confirm:
        raise typer.Abort()

    from water_companion.settings.config import reset_config
    reset_config()
    console.print("[green]✓[/green] Settings reset to defaults.")


@app.command()
def version() -> None:
    """Print the current version."""
    console.print(f"💧 [bold cyan]{APP_NAME}[/bold cyan] v[bold]{APP_VERSION}[/bold]")


# ─────────────────────────────────────────────────────────────────────────────
# GUI launcher
# ─────────────────────────────────────────────────────────────────────────────

def _launch_gui() -> None:
    """Import and run the GUI application."""
    # Check if already running
    if _is_running():
        console.print(f"[yellow]⚠[/yellow] {APP_NAME} is already running. Check your system tray.")
        _send_ipc("open")
        return

    console.print(f"💧 Starting [bold cyan]{APP_NAME}[/bold cyan] v{APP_VERSION}...")
    from water_companion.main import run_app
    run_app()
