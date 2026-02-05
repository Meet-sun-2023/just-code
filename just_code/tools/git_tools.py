"""Git operations tools for Just Code."""

import subprocess
from pathlib import Path
from langchain_core.tools import tool

from just_code.utils import get_logger

logger = get_logger(__name__)


def _run_git_command(args: list[str], cwd: str | None = None) -> tuple[bool, str]:
    """Run a git command and return (success, output).

    Args:
        args: Git command arguments (e.g., ["status", "--short"])
        cwd: Working directory (defaults to current directory)

    Returns:
        Tuple of (success: bool, output: str)
    """
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=False,
            cwd=cwd,
        )
        return result.returncode == 0, result.stdout or result.stderr
    except FileNotFoundError:
        return False, "Git is not installed or not in PATH"
    except Exception as e:
        return False, str(e)


def _is_git_repo(cwd: str | None = None) -> bool:
    """Check if current directory is a git repository."""
    success, _ = _run_git_command(["rev-parse", "--is-inside-work-tree"], cwd=cwd)
    return success


@tool
def git_status() -> str:
    """Get current git status showing modified, staged, and untracked files.

    Returns:
        Git status output showing the working tree status
    """
    if not _is_git_repo():
        return "Not a git repository"

    success, output = _run_git_command(["status", "--short"])
    if success and not output.strip():
        return "Working tree is clean"

    if success:
        # Get detailed status if short status is empty
        if not output.strip():
            success, output = _run_git_command(["status"])

    return output if success else f"Error: {output}"


@tool
def git_diff(files: str = "") -> str:
    """Show changes between commits, commit and working tree, etc.

    Args:
        files: Optional space-separated list of files to diff (e.g., "file1.py file2.py")

    Returns:
        Git diff output showing the changes
    """
    if not _is_git_repo():
        return "Not a git repository"

    args = ["diff"]
    if files:
        args.extend(files.split())

    success, output = _run_git_command(args)
    return output if success else f"Error: {output}"


@tool
def git_diff_staged(files: str = "") -> str:
    """Show changes that are staged for commit.

    Args:
        files: Optional space-separated list of files to diff (e.g., "file1.py file2.py")

    Returns:
        Git diff --staged output showing staged changes
    """
    if not _is_git_repo():
        return "Not a git repository"

    args = ["diff", "--staged"]
    if files:
        args.extend(files.split())

    success, output = _run_git_command(args)
    return output if success else f"Error: {output}"


@tool
def git_add(files: str) -> str:
    """Stage files for commit.

    Args:
        files: Space-separated list of files to stage (e.g., "file1.py file2.py")
               Use "." to stage all files

    Returns:
        Success message or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not files or not files.strip():
        return "Error: No files specified"

    args = ["add"] + files.split()
    success, output = _run_git_command(args)

    if success:
        # Show what was staged
        status_success, status_output = _run_git_command(["status", "--short"])
        if status_success:
            return f"Files staged successfully.\n\nCurrent status:\n{status_output}"
        return "Files staged successfully"
    return f"Error: {output}"


@tool
def git_restore(files: str) -> str:
    """Restore working tree files to their original content (discard changes).

    Args:
        files: Space-separated list of files to restore (e.g., "file1.py file2.py")
               Use "." to restore all files in current directory

    Returns:
        Success message or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not files or not files.strip():
        return "Error: No files specified"

    args = ["restore"] + files.split()
    success, output = _run_git_command(args)

    if success:
        return f"Restored files: {files}"
    return f"Error: {output}"


@tool
def git_restore_staged(files: str) -> str:
    """Unstage files but keep their changes (remove from staging area).

    Args:
        files: Space-separated list of files to unstage

    Returns:
        Success message or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not files or not files.strip():
        return "Error: No files specified"

    args = ["restore", "--staged"] + files.split()
    success, output = _run_git_command(args)

    if success:
        return f"Unstaged files: {files}"
    return f"Error: {output}"


@tool
def git_commit(message: str) -> str:
    """Create a new commit with staged changes.

    Args:
        message: Commit message (e.g., "Add new feature" or "Fix bug in login")

    Returns:
        Success message with commit info or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not message or not message.strip():
        return "Error: Commit message is required"

    args = ["commit", "-m", message]
    success, output = _run_git_command(args)

    if success:
        # Get commit info
        info_success, info_output = _run_git_command(["log", "-1", "--oneline"])
        if info_success:
            return f"Commit created:\n{info_output}"
        return "Commit created successfully"
    return f"Error: {output}"


@tool
def git_log(max_count: int = 10) -> str:
    """Show commit logs.

    Args:
        max_count: Maximum number of commits to show (default: 10)

    Returns:
        Git log output
    """
    if not _is_git_repo():
        return "Not a git repository"

    args = ["log", "--oneline", f"-{max_count}"]
    success, output = _run_git_command(args)
    return output if success else f"Error: {output}"


@tool
def git_branch() -> str:
    """List all branches and show current branch.

    Returns:
        List of branches with current branch highlighted
    """
    if not _is_git_repo():
        return "Not a git repository"

    success, output = _run_git_command(["branch", "-a"])
    return output if success else f"Error: {output}"


@tool
def git_checkout(branch: str) -> str:
    """Switch to a different branch.

    Args:
        branch: Branch name to checkout (e.g., "main", "develop")

    Returns:
        Success message or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not branch or not branch.strip():
        return "Error: Branch name is required"

    args = ["checkout", branch.strip()]
    success, output = _run_git_command(args)

    if success:
        # Show current branch
        status_success, status_output = _run_git_command(["branch", "--show-current"])
        if status_success:
            return f"Switched to branch: {status_output.strip()}"
        return f"Switched to branch: {branch}"
    return f"Error: {output}"


@tool
def git_branch_create(branch: str) -> str:
    """Create a new branch.

    Args:
        branch: Name for the new branch (e.g., "feature/new-function")

    Returns:
        Success message or error
    """
    if not _is_git_repo():
        return "Not a git repository"

    if not branch or not branch.strip():
        return "Error: Branch name is required"

    args = ["checkout", "-b", branch.strip()]
    success, output = _run_git_command(args)

    if success:
        return f"Created and switched to new branch: {branch}"
    return f"Error: {output}"


# Export all tools as a list for easy integration
git_tools = [
    git_status,
    git_diff,
    git_diff_staged,
    git_add,
    git_restore,
    git_restore_staged,
    git_commit,
    git_log,
    git_branch,
    git_checkout,
    git_branch_create,
]
