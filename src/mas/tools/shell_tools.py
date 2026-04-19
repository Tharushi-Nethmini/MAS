from __future__ import annotations

import subprocess


_ALLOWED_PREFIXES: tuple[str, ...] = (
    "Get-ChildItem",
    "dir",
    "Get-Date",
    "Get-Location",
    "pwd",
)


def run_safe_shell(command: str) -> str:
    """Execute only allowlisted read-only PowerShell commands.

    Args:
        command: PowerShell command string.

    Returns:
        Command stdout/stderr combined text.

    Raises:
        ValueError: If command is not allowlisted.
        RuntimeError: If command execution fails unexpectedly.
    """

    normalized = command.strip()
    if not normalized:
        raise ValueError("Command cannot be empty.")

    if not normalized.startswith(_ALLOWED_PREFIXES):
        raise ValueError("Command not allowed. Use read-only allowlisted commands only.")

    completed = subprocess.run(
        ["powershell", "-NoProfile", "-Command", normalized],
        check=False,
        capture_output=True,
        text=True,
        timeout=10,
    )

    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0:
        raise RuntimeError(f"Command failed ({completed.returncode}): {output.strip()}")
    return output.strip()
