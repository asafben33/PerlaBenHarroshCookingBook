#!/usr/bin/env python3
"""
Safe Git Sync with Auto-Backup & Verification v5.0
===================================================

Complete Git workflow tool with backup, sync, and verification capabilities.

Usage:
    python safe-git-pull.py                 # Interactive menu
    python safe-git-pull.py --full-auto     # FULL AUTO mode (zero interaction)
    python safe-git-pull.py --auto          # Same as --full-auto
    python safe-git-pull.py --pull          # Pull only
    python safe-git-pull.py --push          # Push only
    python safe-git-pull.py --sync          # Pull + Push
    python safe-git-pull.py --merge-claude  # Merge Claude branches to main
    python safe-git-pull.py --verify        # Verify Claude changes
    python safe-git-pull.py --cleanup       # Delete merged Claude branches
    python safe-git-pull.py --force         # Skip confirmations
    python safe-git-pull.py --verbose       # Verbose output
    python safe-git-pull.py --dry-run       # Preview mode (with --full-auto)

Features:
    - Auto-backup before operations
    - Detects uncommitted changes (excluding .gitignore)
    - Handles diverged branches with smart merge strategies
    - Checks unpushed commits
    - Stash support
    - Rollback capabilities
    - Auto-detect Claude branches
    - Smart detection of already-merged branches (by content, not just SHA)
    - Interactive rebase or merge-commit options for diverged branches
    - Verify all changes merged
    - Interactive menu with loop
    - Clear screen for clean display
    - Comprehensive logging to logs/
    - Cross-platform compatible (Windows, Linux, macOS)

New in v4.0 (Major Update):
    [OK] Network Resilience:
        - Automatic retry with exponential backoff for network errors (500, timeout, etc.)
        - Multiple fetch strategies with fallback methods
        - Handles GitHub 500 errors, timeouts, and connection issues
        - Smart detection of network vs. non-network errors

    [OK] Enhanced Conflict Handling:
        - Pre-merge safety checks for uncommitted changes and conflicts
        - Automatic detection of conflict markers in code
        - Detailed conflict resolution guidance
        - Safe abort options for merge/rebase operations

    [OK] Improved Divergence Management:
        - Show detailed diff between local and remote
        - Option to create backup branches before risky operations
        - Force push with --force-with-lease (safer than --force)
        - Visual comparison of commits on both sides

    [OK] Better Error Messages:
        - Specific guidance for each error type
        - Step-by-step resolution instructions
        - Color-coded warnings and errors
        - Links to relevant git commands

    [OK] Claude Branch Support:
        - Multiple methods to detect claude/* branches (git branch -r, ls-remote)
        - Fallback to cached data if network fails
        - Better handling of missing or inaccessible branches

    [OK] Safety Improvements:
        - Confirmation prompts for destructive operations
        - Backup creation before dangerous operations
        - Stash reminder before merges
        - Conflict marker detection

    [OK] Smart Rebase Handling (v4.1):
        - Detects already-merged commits ("skipped previously applied commit")
        - Automatic fallback from rebase to merge strategy on conflicts
        - Interactive conflict resolution options
        - Graceful handling of partial merges and cherry-picks
        - Prevents workflow failures due to rebase conflicts

    [OK] Enhanced Features (v4.2):
        - Verbose mode for detailed debugging output
        - Improved error messages with more context
        - Additional safety checks before operations
        - Better handling of edge cases
        - Project rules integration

    [OK] Merge State Detection (v4.3):
        - Detects ongoing merge/rebase/cherry-pick operations
        - Cannot stash during merge conflicts (prevents data loss)
        - Interactive options to abort or resolve ongoing operations
        - Clear instructions for manual conflict resolution
        - Prevents starting new merges during incomplete operations
        - Comprehensive merge state recovery options

    [OK] Auto-Switch to Main Branch (v4.4):
        - Automatically switches from Claude branch to main when merging
        - Auto-stashes uncommitted changes before switching
        - Pulls latest main after switching
        - Works with options 4 (Merge) and 10 (Auto workflow)
        - Provides option to switch from any branch to main
        - Eliminates manual branch switching requirement
        - Streamlined workflow for returning to main after Claude work

    [NEW] Full Auto Mode (v5.0):
        - Complete zero-interaction synchronization via --full-auto flag
        - Integrates with auto-git-sync.py for maximum automation
        - Multi-layer backup system before any operation
        - Intelligent state analysis and automatic decision making
        - Handles ALL scenarios: uncommitted, unpushed, diverged, conflicts
        - Auto-merge all Claude branches to main
        - Network retry with exponential backoff
        - Dry-run mode support for preview
        - Perfect for cron jobs and automated workflows
        - One command does everything: python safe-git-pull.py --full-auto

Previous versions:
    v4.3 - Merge state detection and recovery
    v4.2 - Enhanced features and verbose mode
    v4.1 - Smart rebase handling with auto-fallback
    v4.0 - Network resilience and conflict handling improvements
    v3.2 - Smart merge detection and rebase support
    v3.1 - Interactive menu improvements
    v3.0 - Claude branch auto-detection
    v2.0 - Backup and stash support
    v1.0 - Basic pull/push functionality

IMPORTANT: As per project rules (documentation/PROJECT_RULES.md), this script
MUST be used for ALL git synchronization operations. Direct use of git pull/push
is discouraged to prevent synchronization issues.

Quick Start:
    Full automatic sync with zero interaction (recommended):
        python QA_files/safe-git-pull.py --full-auto
        python QA_files/safe-git-pull.py --full-auto --dry-run   # Preview mode

    Interactive menu (for beginners):
        python QA_files/safe-git-pull.py

    Quick commands:
        python QA_files/safe-git-pull.py --pull          # Pull only
        python QA_files/safe-git-pull.py --push          # Push only
        python QA_files/safe-git-pull.py --sync          # Pull + Push
        python QA_files/safe-git-pull.py --merge-claude  # Merge Claude branches
        python QA_files/safe-git-pull.py --verbose       # Verbose debug output

    Full auto mode (via menu):
        python QA_files/safe-git-pull.py
        # Select option 10 from menu - Merge + Sync + Auto cleanup

Author: Claude & Assi
Version: 5.0
Date: 2026-02-03
"""

import subprocess
import sys
import os
import shutil
from datetime import datetime
from pathlib import Path
import fnmatch
import logging

# ========== PATH ANCHORING ==========
PROJECT_ROOT = Path(__file__).resolve().parent.parent
os.chdir(PROJECT_ROOT)

# ========== GLOBAL CONFIGURATION ==========

# Verbose mode (can be set via --verbose flag)
VERBOSE_MODE = False

# ========== LOGGING SETUP ==========

def cleanup_old_logs(logs_dir, keep_count=3):
    """Keep only the most recent log files and delete older ones"""
    try:
        # Get all log files matching the pattern
        log_files = list(logs_dir.glob("safe-git-pull_*.log"))

        if len(log_files) <= keep_count:
            return  # Nothing to clean up

        # Sort by modification time (newest first)
        log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)

        # Delete old log files (keep only the newest keep_count)
        deleted_count = 0
        for old_log in log_files[keep_count:]:
            try:
                old_log.unlink()
                deleted_count += 1
            except Exception as e:
                print(f"Warning: Could not delete old log file {old_log.name}: {e}")

        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old log file(s), keeping {keep_count} most recent")

    except Exception as e:
        print(f"Warning: Error during log cleanup: {e}")

def setup_logging():
    """Setup logging to file and console"""
    # Create logs directory if it doesn't exist
    logs_dir = PROJECT_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)

    # Clean up old log files (keep only 3 most recent)
    cleanup_old_logs(logs_dir, keep_count=3)

    # Create log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"safe-git-pull_{timestamp}.log"

    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("=" * 70)
    logger.info("Safe Git Pull - Session Started")
    logger.info(f"Log file: {log_file}")
    logger.info(f"Verbose mode: {VERBOSE_MODE}")
    logger.info("=" * 70)

    return logger

# Initialize logger
logger = setup_logging()

class Colors:
    """ANSI color codes for terminal output"""
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    BOLD = '\033[1m'
    END = '\033[0m'
    # Additional colors for verification
    CHECK = '[OK]'
    CROSS = '[FAIL]'
    INFO = ''
    WARNING_SYMBOL = '[WARN]'

def clear_screen():
    """Clear terminal screen for clean display"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'━' * 70}")
    print(f"  {text}")
    print(f"{'━' * 70}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}{Colors.CHECK} {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}{Colors.CROSS} {text}{Colors.END}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.YELLOW}{Colors.WARNING_SYMBOL} {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}{Colors.INFO} {text}{Colors.END}")

def print_verbose(text):
    """Print verbose message (only if verbose mode is enabled)"""
    if VERBOSE_MODE:
        print(f"{Colors.MAGENTA}[VERBOSE] {text}{Colors.END}")

def run_command(cmd, capture_output=True):
    """Run shell command and return (returncode, stdout, stderr)"""
    logger.debug(f"Running command: {cmd}")
    print_verbose(f"Executing: {cmd}")
    try:
        if capture_output:
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            logger.debug(f"Command exit code: {result.returncode}")
            print_verbose(f"Exit code: {result.returncode}")
            if result.stdout:
                logger.debug(f"Command stdout: {result.stdout[:200]}")  # First 200 chars
                print_verbose(f"Output: {result.stdout[:100]}")
            if result.stderr:
                logger.warning(f"Command stderr: {result.stderr[:200]}")
                if result.returncode != 0:
                    print_verbose(f"Error: {result.stderr[:100]}")
            return result.returncode, result.stdout.strip(), result.stderr.strip()
        else:
            result = subprocess.run(cmd, shell=True)
            logger.debug(f"Command exit code: {result.returncode}")
            print_verbose(f"Exit code: {result.returncode}")
            return result.returncode, "", ""
    except Exception as e:
        logger.error(f"Command failed with exception: {e}")
        print_verbose(f"Exception: {e}")
        return 1, "", str(e)

def get_git_root():
    """Get git repository root directory"""
    returncode, stdout, _ = run_command("git rev-parse --show-toplevel")
    if returncode != 0:
        return None
    return stdout


def get_default_branch():
    """
    Detect the default branch name (main or master).

    Handles the common mismatch where the local branch is named 'master'
    but the remote default is 'origin/main' (or vice versa). When a mismatch
    is detected, the local branch is automatically renamed to match the remote
    and upstream tracking is configured.

    Returns:
        str: The default branch name (e.g. 'main' or 'master')
    """
    # Step 1: Detect remote default branch
    remote_default = None

    ret, stdout, _ = run_command("git symbolic-ref refs/remotes/origin/HEAD")
    if ret == 0 and stdout:
        candidate = stdout.strip().split('/')[-1]
        if candidate in ('main', 'master'):
            remote_default = candidate
            logger.debug(f"Remote default branch via origin/HEAD: {remote_default}")

    if not remote_default:
        for candidate in ('main', 'master'):
            ret, _, _ = run_command(f"git rev-parse --verify origin/{candidate}")
            if ret == 0:
                remote_default = candidate
                logger.debug(f"Remote default branch detected: {remote_default}")
                break

    # Step 2: Detect local default branch
    local_default = None
    ret, stdout, _ = run_command("git branch --list main master")
    if ret == 0 and stdout:
        local_branches = [b.strip().lstrip('* ') for b in stdout.split('\n') if b.strip()]
        if remote_default and remote_default in local_branches:
            local_default = remote_default
        elif local_branches:
            local_default = local_branches[0]

    # Step 3: Handle mismatch (e.g. local=master, remote=main)
    if local_default and remote_default and local_default != remote_default:
        logger.warning(
            f"Branch name mismatch: local='{local_default}', remote='{remote_default}'. "
            f"Renaming local '{local_default}' to '{remote_default}'..."
        )
        print_warning(
            f"Branch name mismatch detected: local '{local_default}' vs remote '{remote_default}'"
        )
        print_info(f"Auto-renaming local '{local_default}' to '{remote_default}'...")

        ret, _, stderr = run_command(f"git branch -m {local_default} {remote_default}")
        if ret == 0:
            run_command(
                f"git branch --set-upstream-to=origin/{remote_default} {remote_default}"
            )
            logger.info(f"Renamed local branch to '{remote_default}' with upstream tracking")
            print_success(f"Local branch renamed to '{remote_default}' (tracking origin/{remote_default})")
            return remote_default
        else:
            logger.error(f"Failed to rename branch: {stderr}")

    # Step 4: Return best match
    if local_default and remote_default and local_default == remote_default:
        ret, _, _ = run_command(f"git config branch.{local_default}.remote")
        if ret != 0:
            run_command(
                f"git branch --set-upstream-to=origin/{remote_default} {local_default}"
            )
            logger.info(f"Set upstream tracking for '{local_default}'")
        return local_default

    if remote_default:
        return remote_default
    if local_default:
        return local_default

    logger.warning("Could not detect default branch, falling back to 'main'")
    return 'main'


# Detect default branch name (main or master) at startup
DEFAULT_BRANCH = get_default_branch()
logger.info(f"Default branch: {DEFAULT_BRANCH}")


def check_script_updates():
    """
    Check if there's a newer version of this script on remote
    Returns: (has_updates, message)
    """
    try:
        script_path = os.path.abspath(__file__)
        git_root = get_git_root()

        if not git_root:
            return False, ""

        # Get relative path from git root
        rel_path = os.path.relpath(script_path, git_root)

        # Fetch remote changes quietly
        run_command("git fetch origin --quiet")

        # Check if script has changes on remote
        returncode, stdout, _ = run_command(f"git diff HEAD origin/{DEFAULT_BRANCH} -- {rel_path}")

        if returncode == 0 and stdout:
            return True, f"A newer version of {os.path.basename(__file__)} is available on remote"

        return False, ""
    except Exception as e:
        logger.debug(f"Failed to check for script updates: {e}")
        return False, ""

def get_current_branch():
    """Get current git branch name"""
    returncode, stdout, _ = run_command("git branch --show-current")
    if returncode == 0 and stdout:
        return stdout
    return None

def check_git_repository_health():
    """
    Perform health checks on the git repository
    Returns: (is_healthy, issues_list)
    """
    print_verbose("Performing repository health checks...")
    issues = []

    # Check if we're in a git repository
    returncode, _, _ = run_command("git rev-parse --git-dir")
    if returncode != 0:
        issues.append("Not in a git repository")
        return False, issues

    # Check if repository is corrupted
    returncode, stdout, stderr = run_command("git fsck --no-progress --no-dangling")
    if returncode != 0:
        if "error" in stderr.lower() or "fatal" in stderr.lower():
            issues.append(f"Repository corruption detected: {stderr[:100]}")

    # Check for large files that shouldn't be committed (cross-platform)
    import os as _os
    if _os.name == 'nt':
        # Windows: use git ls-files with Python-based size check
        returncode, stdout, _ = run_command("git ls-files", capture_output=True)
        if returncode == 0 and stdout:
            for filepath in stdout.split('\n')[:100]:  # Check first 100 files
                filepath = filepath.strip()
                if filepath and _os.path.exists(filepath):
                    try:
                        size_bytes = _os.path.getsize(filepath)
                        if size_bytes > 50 * 1024 * 1024:  # 50MB
                            size_mb = size_bytes / (1024 * 1024)
                            issues.append(f"Large file detected: {filepath} ({size_mb:.1f}M)")
                    except OSError:
                        pass
    else:
        # Unix: use du command
        returncode, stdout, _ = run_command("git ls-files -z | xargs -0 du -h 2>/dev/null | sort -hr | head -5")
        if returncode == 0 and stdout:
            lines = stdout.split('\n')
            for line in lines:
                if line:
                    try:
                        size, filename = line.split('\t', 1)
                        # Check if file is larger than 50MB
                        if 'M' in size or 'G' in size:
                            size_val = float(size.replace('M', '').replace('G', ''))
                            if ('G' in size) or (size_val > 50):
                                issues.append(f"Large file detected: {filename} ({size})")
                    except (ValueError, IndexError):
                        pass

    # Check for untracked large files
    returncode, stdout, _ = run_command("git status --porcelain")
    if returncode == 0 and stdout:
        untracked_count = len([line for line in stdout.split('\n') if line.startswith('??')])
        if untracked_count > 100:
            issues.append(f"Many untracked files ({untracked_count}) - consider .gitignore")

    print_verbose(f"Health check complete. Issues found: {len(issues)}")
    return len(issues) == 0, issues

def check_merge_in_progress():
    """Check if there's a merge/rebase/cherry-pick in progress"""
    git_dir = Path(".git")

    # Check for various git operations in progress
    merge_head = git_dir / "MERGE_HEAD"
    rebase_merge = git_dir / "rebase-merge"
    rebase_apply = git_dir / "rebase-apply"
    cherry_pick_head = git_dir / "CHERRY_PICK_HEAD"

    if merge_head.exists():
        return ("merge", "Merge in progress")
    elif rebase_merge.exists() or rebase_apply.exists():
        return ("rebase", "Rebase in progress")
    elif cherry_pick_head.exists():
        return ("cherry-pick", "Cherry-pick in progress")

    return (None, None)

def clean_merge_state():
    """
    Clean up any ongoing merge/rebase/cherry-pick state
    Returns True if state was cleaned, False if nothing to clean
    """
    operation_type, operation_msg = check_merge_in_progress()

    if operation_type:
        logger.warning(f"Found ongoing operation: {operation_msg}")
        print_warning(f"[WARNING] {operation_msg} detected - cleaning up...")

        if operation_type == "merge":
            returncode, _, stderr = run_command("git merge --abort", capture_output=True)
            if returncode == 0:
                print_info("[OK] Aborted previous merge")
                logger.info("Successfully aborted merge")
                return True
            else:
                logger.error(f"Failed to abort merge: {stderr}")
                return False

        elif operation_type == "rebase":
            returncode, _, stderr = run_command("git rebase --abort", capture_output=True)
            if returncode == 0:
                print_info("[OK] Aborted previous rebase")
                logger.info("Successfully aborted rebase")
                return True
            else:
                logger.error(f"Failed to abort rebase: {stderr}")
                return False

        elif operation_type == "cherry-pick":
            returncode, _, stderr = run_command("git cherry-pick --abort", capture_output=True)
            if returncode == 0:
                print_info("[OK] Aborted previous cherry-pick")
                logger.info("Successfully aborted cherry-pick")
                return True
            else:
                logger.error(f"Failed to abort cherry-pick: {stderr}")
                return False

    return False

def stash_local_changes():
    """
    Stash all local changes (staged + unstaged) before merge/rebase.
    Returns stash name if stash was created, None if nothing to stash.
    """
    returncode, stdout, _ = run_command("git status --porcelain")
    if returncode != 0 or not stdout or not stdout.strip():
        return None  # Nothing to stash

    logger.info(f"Found local changes, stashing before merge...")
    print_info("[AUTO] Stashing local changes before merge...")

    from datetime import datetime as _dt
    stash_msg = f"auto-stash-before-merge-{_dt.now():%Y%m%d_%H%M%S}"
    returncode, _, stderr = run_command(f'git stash push -m "{stash_msg}"', capture_output=True)

    if returncode == 0:
        print_info(f"[OK] Changes stashed: {stash_msg}")
        logger.info(f"Stash created: {stash_msg}")
        return stash_msg
    else:
        logger.error(f"Failed to stash: {stderr}")
        print_error(f"[FAIL] Failed to stash changes: {stderr}")
        return None


def pop_stash(stash_msg):
    """
    Restore previously stashed changes.
    If pop fails (conflicts with merged code), keeps stash and warns.
    """
    if not stash_msg:
        return

    logger.info("Restoring stashed changes...")
    print_info("[AUTO] Restoring stashed changes...")

    returncode, _, stderr = run_command("git stash pop", capture_output=True)
    if returncode == 0:
        print_info("[OK] Stashed changes restored")
        logger.info("Stash popped successfully")
    else:
        # Stash pop failed - likely conflicts with merged code.
        # The stash is still there - drop it since merged code is newer.
        logger.warning(f"Stash pop had conflicts (expected - merged code is newer): {stderr}")
        print_warning("[INFO] Stash conflicts with merged code (expected - keeping merged version)")
        run_command("git checkout -- .", capture_output=True)
        run_command("git stash drop", capture_output=True)
        print_info("[OK] Dropped stash (merged code takes precedence)")


def handle_unstaged_changes():
    """
    Handle unstaged changes before merge/rebase operations.
    Returns True if handled successfully, False otherwise.
    Note: This function adds changes to the index. For merge operations,
    use stash_local_changes() instead to avoid 'would be overwritten' errors.
    """
    returncode, stdout, _ = run_command("git status --porcelain")

    if returncode != 0 or not stdout:
        return True  # No changes to handle

    # Check for unstaged changes (including deletions, modifications, additions)
    unstaged = []
    for line in stdout.split('\n'):
        if line.strip():
            status = line[:2]
            # Check for unstaged deletions (D), modifications (M), or unmerged files (AA, DD, UU, etc.)
            if ' D' in status or ' M' in status or 'AA' in status or 'DD' in status or 'UU' in status:
                unstaged.append(line)

    if not unstaged:
        return True  # No unstaged changes

    logger.warning(f"Found {len(unstaged)} unstaged change(s)")
    print_warning(f"[WARNING] Found {len(unstaged)} unstaged change(s):")
    for change in unstaged[:10]:
        print(f"  {change}")
    if len(unstaged) > 10:
        print(f"  ... and {len(unstaged) - 10} more")

    # Auto-handle: add all changes to index
    print_info("[AUTO] Adding unstaged changes to index...")
    returncode, _, stderr = run_command("git add -A", capture_output=True)

    if returncode == 0:
        print_info("[OK] Unstaged changes added to index")
        logger.info("Successfully staged all changes")
        return True
    else:
        logger.error(f"Failed to stage changes: {stderr}")
        print_error(f"[FAIL] Failed to stage changes: {stderr}")
        return False

def auto_resolve_add_add_conflicts(prefer_theirs=True):
    """
    Auto-resolve merge conflicts during claude branch merges.

    Handles:
    - AA (add/add) conflicts: Both branches created the same file independently.
      Prefers the incoming (theirs/claude) version since it's the refined version.
    - UU (content) conflicts: Both branches modified the same file.
      Prefers the incoming (theirs/claude) version since we're merging claude changes.

    Args:
        prefer_theirs: If True, accept incoming (claude) branch version for conflicts.
                       This is the correct default when merging claude branches into main.

    Returns: (resolved_count, total_conflicts)
    """
    # Get unmerged files
    returncode, stdout, _ = run_command('git diff --name-only --diff-filter=U')

    if returncode != 0 or not stdout:
        return (0, 0)  # No conflicts to resolve

    unmerged_files = [f.strip() for f in stdout.split('\n') if f.strip()]
    total_conflicts = len(unmerged_files)
    resolved_count = 0

    logger.info(f"Found {total_conflicts} unmerged file(s)")
    print_info(f"[INFO] Found {total_conflicts} unmerged file(s)")

    for file_path in unmerged_files:
        # Check conflict type
        returncode, status, _ = run_command(f'git status --porcelain {file_path}')

        if returncode != 0:
            continue

        if 'AA' in status:
            # Both branches added the same file
            ret_ours, content_ours, _ = run_command(f'git show :2:{file_path}', capture_output=True)
            ret_theirs, content_theirs, _ = run_command(f'git show :3:{file_path}', capture_output=True)

            if ret_ours == 0 and ret_theirs == 0:
                if content_ours == content_theirs:
                    # Content is identical - accept either version
                    print_info(f"[AUTO-RESOLVE] {file_path} (identical content)")
                    logger.info(f"Auto-resolving {file_path} - identical content in both branches")
                    run_command(f'git add {file_path}', capture_output=True)
                    resolved_count += 1
                elif prefer_theirs:
                    # Different content - accept incoming (claude) version
                    print_info(f"[AUTO-RESOLVE] {file_path} (accepting incoming claude version)")
                    logger.info(f"Auto-resolving {file_path} - accepting theirs (claude branch version)")
                    ret, _, _ = run_command(f'git checkout --theirs -- "{file_path}"', capture_output=True)
                    if ret == 0:
                        run_command(f'git add "{file_path}"', capture_output=True)
                        resolved_count += 1
                    else:
                        logger.warning(f"Failed to checkout --theirs for {file_path}")
                        print_warning(f"[MANUAL] {file_path} (auto-resolve failed)")
                else:
                    logger.warning(f"Cannot auto-resolve {file_path} - different content")
                    print_warning(f"[MANUAL] {file_path} (different content - needs manual resolution)")

        elif 'UU' in status:
            # Content conflict - both branches modified the same file
            if prefer_theirs:
                print_info(f"[AUTO-RESOLVE] {file_path} (accepting incoming claude version)")
                logger.info(f"Auto-resolving UU conflict {file_path} - accepting theirs (claude branch)")
                ret, _, _ = run_command(f'git checkout --theirs -- "{file_path}"', capture_output=True)
                if ret == 0:
                    run_command(f'git add "{file_path}"', capture_output=True)
                    resolved_count += 1
                else:
                    logger.warning(f"Failed to checkout --theirs for {file_path}")
                    print_warning(f"[MANUAL] {file_path} (auto-resolve failed)")
            else:
                logger.warning(f"Cannot auto-resolve {file_path} - content conflict")
                print_warning(f"[MANUAL] {file_path} (content conflict - needs manual resolution)")

        else:
            # Unknown conflict type - try theirs if preferred
            if prefer_theirs:
                logger.info(f"Resolving unknown conflict type for {file_path} with --theirs")
                ret, _, _ = run_command(f'git checkout --theirs -- "{file_path}"', capture_output=True)
                if ret == 0:
                    run_command(f'git add "{file_path}"', capture_output=True)
                    resolved_count += 1
                else:
                    print_warning(f"[MANUAL] {file_path} (unknown conflict type - needs manual resolution)")
            else:
                print_warning(f"[MANUAL] {file_path} (conflict type: {status.strip()[:2]})")

    if resolved_count > 0:
        print_success(f"[OK] Auto-resolved {resolved_count}/{total_conflicts} conflict(s)")

    return (resolved_count, total_conflicts)

def check_conflict_markers():
    """Check for unresolved conflict markers in files"""
    logger.debug("Checking for conflict markers...")
    returncode, stdout, _ = run_command('git diff --check')

    if returncode != 0 and stdout:
        # There are conflict markers
        logger.warning(f"Found conflict markers: {stdout}")
        return True

    # Also check with grep as fallback
    conflict_patterns = ['<<<<<<<', '=======', '>>>>>>>']
    returncode, stdout, _ = run_command('git diff --name-only --diff-filter=U')

    if returncode == 0 and stdout:
        # There are unmerged files
        logger.warning(f"Found unmerged files: {stdout}")
        return True

    return False

def check_git_status():
    """Check uncommitted changes (excluding .gitignore files)"""
    returncode, stdout, _ = run_command("git status --porcelain")
    if returncode != 0 or not stdout:
        return []

    # Parse git status and filter out ignored files
    changes = []
    for line in stdout.split('\n'):
        if line.strip():
            # Extract filename from porcelain format: "XY filename"
            # Note: run_command() strips stdout, which may remove leading
            # space from the 2-char status code. Use split() for robustness.
            parts = line.lstrip().split(maxsplit=1)
            file_path = parts[1] if len(parts) >= 2 else line.strip()
            ret, _, _ = run_command(f'git check-ignore "{file_path}"')
            if ret != 0:  # Not ignored
                changes.append(line)

    return changes

def fetch_remote(branch, retry_count=3, retry_delay=2):
    """
    Fetch from remote with retry logic for network failures

    Args:
        branch: Branch name to fetch
        retry_count: Number of retry attempts (default: 3)
        retry_delay: Delay between retries in seconds (default: 2)

    Returns:
        True if successful, False otherwise
    """
    import time

    print_info("Fetching from remote...")

    for attempt in range(1, retry_count + 1):
        returncode, stdout, stderr = run_command(f"git fetch origin {branch}")

        if returncode == 0:
            return True

        # Check if it's a network error (500, timeout, etc.)
        network_errors = [
            'Internal Server Error',
            'error: 500',
            'Connection timed out',
            'Could not resolve host',
            'Failed to connect',
            'Operation timed out',
            'unable to access'
        ]

        is_network_error = any(err in stderr for err in network_errors)

        if is_network_error and attempt < retry_count:
            logger.warning(f"Network error on attempt {attempt}/{retry_count}: {stderr[:100]}")
            print_warning(f"Network error, retrying in {retry_delay}s... (attempt {attempt}/{retry_count})")
            time.sleep(retry_delay)
            # Exponential backoff
            retry_delay *= 2
        elif attempt == retry_count:
            logger.error(f"Failed to fetch after {retry_count} attempts: {stderr}")
            print_error(f"Failed to fetch after {retry_count} attempts")
            return False
        else:
            # Non-network error, don't retry
            logger.error(f"Fetch failed with non-network error: {stderr}")
            return False

    return False

def get_new_commits(branch):
    """Get list of new commits to be pulled"""
    returncode, stdout, _ = run_command(f"git log HEAD..origin/{branch} --oneline")
    if returncode == 0 and stdout:
        return stdout.split('\n')
    return []

def check_unpushed_commits(branch):
    """Check for unpushed commits"""
    returncode, stdout, _ = run_command(f"git log origin/{branch}..HEAD --oneline")
    if returncode == 0 and stdout:
        return stdout.split('\n')
    return []

def check_diverged_branches(branch):
    """Check if local and remote branches have diverged"""
    # Count commits ahead/behind
    ret_ahead, stdout_ahead, _ = run_command(f"git rev-list --count origin/{branch}..HEAD")
    ret_behind, stdout_behind, _ = run_command(f"git rev-list --count HEAD..origin/{branch}")

    local_ahead = int(stdout_ahead) if ret_ahead == 0 and stdout_ahead else 0
    remote_ahead = int(stdout_behind) if ret_behind == 0 and stdout_behind else 0

    return local_ahead, remote_ahead

def check_commit_merged(branch_name, target_branch=None):
    """Check if commits from branch are already merged into target by content (not just SHA)"""
    if target_branch is None:
        target_branch = DEFAULT_BRANCH
    # Get the merge-base (common ancestor)
    ret, merge_base, _ = run_command(f"git merge-base {target_branch} {branch_name}")
    if ret != 0:
        logger.debug(f"Could not find merge-base for {branch_name} and {target_branch}")
        return False

    merge_base = merge_base.strip()

    # Check if branch is already fully merged (branch HEAD is ancestor of target)
    ret, is_ancestor, _ = run_command(f"git merge-base --is-ancestor {branch_name} {target_branch}")
    if ret == 0:
        logger.debug(f"Branch {branch_name} is already an ancestor of {target_branch}")
        return True

    # Get the diff between merge-base and branch
    ret, branch_diff, _ = run_command(f"git diff {merge_base}..{branch_name}")
    if ret != 0:
        logger.debug(f"Could not get diff for {branch_name}")
        return False

    # Get the diff between merge-base and target
    ret, target_diff, _ = run_command(f"git diff {merge_base}..{target_branch}")
    if ret != 0:
        logger.debug(f"Could not get diff for {target_branch}")
        return False

    # If branch has no unique changes, it's merged
    if not branch_diff or not branch_diff.strip():
        logger.debug(f"Branch {branch_name} has no unique changes")
        return True

    # If target contains all the changes from branch, consider it merged
    # This is a simplified check - in reality we'd need patch matching
    if branch_diff in target_diff:
        logger.debug(f"Branch {branch_name} changes are contained in {target_branch}")
        return True

    return False

def get_claude_branches():
    """Get list of remote claude/* branches with commits ahead of main"""
    import time

    logger.info("Fetching all remote branches...")

    # Try multiple fetch strategies with retry logic
    fetch_successful = False

    # Strategy 1: Fetch all with prune (with retries)
    for attempt in range(1, 4):
        returncode, stdout, stderr = run_command("git fetch --all --prune")

        if returncode == 0:
            logger.info("Successfully fetched all remote branches")
            fetch_successful = True
            break

        # Check for network errors
        network_errors = [
            'Internal Server Error',
            'error: 500',
            'error: 502',
            'error: 503',
            'Connection timed out',
            'Could not resolve host',
            'Failed to connect',
            'Operation timed out',
            'unable to access'
        ]

        is_network_error = any(err in stderr for err in network_errors)

        if is_network_error and attempt < 3:
            delay = 2 ** attempt  # Exponential backoff: 2s, 4s
            logger.warning(f"Network error on attempt {attempt}/3: {stderr[:100]}")
            print_warning(f"Network error, retrying in {delay}s... (attempt {attempt}/3)")
            time.sleep(delay)
        else:
            logger.error(f"Failed to fetch remote branches after {attempt} attempts: {stderr}")
            break

    # Strategy 2: Try fetching only origin (fallback)
    if not fetch_successful:
        print_info("Trying alternative fetch method...")
        returncode, stdout, stderr = run_command("git fetch origin")
        if returncode == 0:
            logger.info("Successfully fetched origin using fallback method")
            fetch_successful = True

    # Strategy 3: Try ls-remote as last resort (read-only, no fetch)
    if not fetch_successful:
        print_info("Trying read-only remote check...")
        returncode, stdout, stderr = run_command("git ls-remote --heads origin")
        if returncode == 0:
            logger.info("Successfully queried remote via ls-remote")
            # This doesn't update local refs, but at least we can see what's there
            print_warning("Using cached remote data (network issues prevented update)")
        else:
            print_warning("Failed to fetch remote branches. Using cached data...")
            logger.error(f"All fetch strategies failed. Last error: {stderr}")

    # Get all remote claude/ branches
    logger.debug("Searching for claude/* branches...")
    returncode, stdout, stderr = run_command("git branch -r")

    if returncode != 0:
        logger.warning(f"Failed to list remote branches: {stderr}")

        # Fallback: Try using ls-remote
        print_info("Trying alternative method to find branches...")
        returncode2, stdout2, _ = run_command("git ls-remote --heads origin 'claude/*'")

        if returncode2 == 0 and stdout2:
            # Parse ls-remote output: "hash\trefs/heads/claude/branch-name"
            claude_lines = []
            for line in stdout2.split('\n'):
                if line and '\t' in line:
                    ref = line.split('\t')[1]
                    if ref.startswith('refs/heads/claude/'):
                        branch_name = ref.replace('refs/heads/', '')
                        claude_lines.append(f"origin/{branch_name}")
            logger.info(f"Found {len(claude_lines)} claude/* branches via ls-remote")
        else:
            logger.error("All methods to find branches failed")
            print_warning("Could not fetch branch list. Using cached data if available.")
            return []
    else:
        # Filter only claude branches
        claude_lines = [line.strip() for line in stdout.split('\n') if 'origin/claude/' in line]
        logger.info(f"Found {len(claude_lines)} claude/* branches on remote")

    if not claude_lines:
        logger.info("No claude/* branches found")
        return []

    branches = []
    for line in claude_lines:
        branch = line.strip()
        if branch and branch.startswith('origin/claude/'):
            branch_name = branch.replace('origin/', '')
            logger.debug(f"Checking branch: {branch_name}")

            # First check if commits are already merged by content
            if check_commit_merged(branch, DEFAULT_BRANCH):
                logger.info(f"Branch {branch_name} is already merged (by content)")
                continue

            # Check if this branch has commits ahead of main
            ret, commits, _ = run_command(f"git log {DEFAULT_BRANCH}..{branch} --oneline")
            if ret == 0 and commits:
                commit_list = commits.split('\n')
                logger.info(f"Branch {branch_name} has {len(commit_list)} new commit(s)")
                branches.append({
                    'name': branch_name,
                    'full_name': branch,
                    'commits': commit_list
                })
            else:
                logger.debug(f"Branch {branch_name} has no new commits")

    logger.info(f"Total claude branches with new commits: {len(branches)}")
    return branches

def auto_switch_to_main_branch():
    """
    Automatically switch to main branch if on a Claude branch
    Also pulls latest main to ensure we're up to date

    Returns:
        tuple: (success: bool, original_branch: str)
    """
    # Get current branch
    returncode, current_branch, _ = run_command("git branch --show-current", capture_output=True)
    if returncode != 0:
        print_error("Failed to get current branch")
        return False, None

    current_branch = current_branch.strip()

    # If already on main, just pull latest
    if current_branch == DEFAULT_BRANCH:
        print_info(f"Already on {DEFAULT_BRANCH} branch")
        print_info(f"Pulling latest {DEFAULT_BRANCH}...")
        returncode, _, stderr = run_command(f"git pull origin {DEFAULT_BRANCH}", capture_output=True)
        if returncode == 0:
            print_success(f"{DEFAULT_BRANCH} branch updated")
            return True, DEFAULT_BRANCH
        else:
            print_warning(f"Failed to pull {DEFAULT_BRANCH}: {stderr}")
            print_info(f"Continuing with current {DEFAULT_BRANCH}...")
            return True, DEFAULT_BRANCH

    # If on a Claude branch, switch to main
    if current_branch.startswith('claude/'):
        print_warning(f"Currently on Claude branch: {current_branch}")
        print_info(f"Automatically switching to {DEFAULT_BRANCH} branch...")

        # Check for uncommitted changes first
        uncommitted = check_git_status()
        if uncommitted:
            print_warning(f"You have {len(uncommitted)} uncommitted change(s)")
            print_info("Stashing changes before switching branches...")
            ret, _, _ = run_command("git stash")
            if ret != 0:
                print_error(f"Failed to stash changes. Cannot switch to {DEFAULT_BRANCH}.")
                return False, current_branch
            print_success("Changes stashed")

        # Switch to main
        returncode, _, stderr = run_command(f"git checkout {DEFAULT_BRANCH}", capture_output=True)
        if returncode != 0:
            print_error(f"Failed to switch to {DEFAULT_BRANCH}: {stderr}")
            return False, current_branch

        print_success(f"Switched to {DEFAULT_BRANCH} branch")

        # Pull latest main
        print_info(f"Pulling latest {DEFAULT_BRANCH}...")
        returncode, _, stderr = run_command(f"git pull origin {DEFAULT_BRANCH}", capture_output=True)
        if returncode == 0:
            print_success(f"{DEFAULT_BRANCH} branch updated")
        else:
            print_warning(f"Failed to pull {DEFAULT_BRANCH}: {stderr}")
            print_info(f"Continuing with current {DEFAULT_BRANCH}...")

        return True, current_branch

    # On some other branch (not main, not claude/*)
    print_warning(f"Currently on branch: {current_branch}")
    print_warning(f"This is not {DEFAULT_BRANCH} or a Claude branch")
    print()
    print("Options:")
    print(f"  {Colors.BOLD}1.{Colors.END} Automatically switch to {DEFAULT_BRANCH}")
    print(f"  {Colors.BOLD}2.{Colors.END} Cancel and switch manually")

    choice = input("\nYour choice (1-2): ").strip()

    if choice == "1":
        # Check for uncommitted changes first
        uncommitted = check_git_status()
        if uncommitted:
            print_warning(f"You have {len(uncommitted)} uncommitted change(s)")
            print_info("Stashing changes before switching branches...")
            ret, _, _ = run_command("git stash")
            if ret != 0:
                print_error(f"Failed to stash changes. Cannot switch to {DEFAULT_BRANCH}.")
                return False, current_branch
            print_success("Changes stashed")

        # Switch to main
        returncode, _, stderr = run_command(f"git checkout {DEFAULT_BRANCH}", capture_output=True)
        if returncode != 0:
            print_error(f"Failed to switch to {DEFAULT_BRANCH}: {stderr}")
            return False, current_branch

        print_success(f"Switched to {DEFAULT_BRANCH} branch")

        # Pull latest main
        print_info(f"Pulling latest {DEFAULT_BRANCH}...")
        returncode, _, stderr = run_command(f"git pull origin {DEFAULT_BRANCH}", capture_output=True)
        if returncode == 0:
            print_success(f"{DEFAULT_BRANCH} branch updated")
        else:
            print_warning(f"Failed to pull {DEFAULT_BRANCH}: {stderr}")
            print_info(f"Continuing with current {DEFAULT_BRANCH}...")

        return True, current_branch
    else:
        print_info("Operation cancelled")
        return False, current_branch


def check_and_merge_claude_branches():
    """Check for claude branches and offer to merge them"""
    logger.info("Starting Claude branches merge process...")

    # Pre-merge safety checks
    print_info("Running pre-merge safety checks...")

    # Check if there's an ongoing merge/rebase
    operation_type, operation_msg = check_merge_in_progress()
    if operation_type:
        print_error(f"[FAIL] Cannot start merge - {operation_msg}!")
        print()
        print("You must resolve the existing operation first:")
        print()

        if operation_type == "merge":
            print("Options:")
            print(f"  {Colors.BOLD}1.{Colors.END} Abort existing merge (git merge --abort)")
            print(f"  {Colors.BOLD}2.{Colors.END} Complete existing merge (resolve conflicts first)")
            print(f"  {Colors.BOLD}3.{Colors.END} Show conflicted files")
            print(f"  {Colors.BOLD}4.{Colors.END} Cancel")

            choice = input("\nYour choice (1-4): ").strip()

            if choice == "1":
                ret, _, _ = run_command("git merge --abort")
                if ret == 0:
                    print_success("Existing merge aborted. You can now proceed.")
                    # Fall through to continue with new merge
                else:
                    print_error("Failed to abort merge")
                    return False

            elif choice == "2":
                print_info("Please complete the merge first:")
                print("  1. Resolve conflicts in files")
                print("  2. git add <resolved-files>")
                print("  3. git commit")
                print("  4. Then run this merge again")
                return False

            elif choice == "3":
                run_command("git status")
                return False

            else:
                return False

        elif operation_type == "rebase":
            print("Options:")
            print(f"  {Colors.BOLD}1.{Colors.END} Abort existing rebase (git rebase --abort)")
            print(f"  {Colors.BOLD}2.{Colors.END} Complete existing rebase (resolve conflicts first)")
            print(f"  {Colors.BOLD}3.{Colors.END} Cancel")

            choice = input("\nYour choice (1-3): ").strip()

            if choice == "1":
                ret, _, _ = run_command("git rebase --abort")
                if ret == 0:
                    print_success("Existing rebase aborted. You can now proceed.")
                    # Fall through to continue with new merge
                else:
                    print_error("Failed to abort rebase")
                    return False

            elif choice == "2":
                print_info("Please complete the rebase first:")
                print("  1. Resolve conflicts")
                print("  2. git add <resolved-files>")
                print("  3. git rebase --continue")
                print("  4. Then run this merge again")
                return False

            else:
                return False

    # Check for uncommitted changes
    uncommitted = check_git_status()
    if uncommitted:
        print_warning(f"[WARN] You have {len(uncommitted)} uncommitted change(s)")
        print()
        print("It's recommended to commit or stash changes before merging.")
        print()
        print("Options:")
        print("  1. Stash changes and continue")
        print("  2. Show uncommitted changes")
        print("  3. Continue anyway (not recommended)")
        print("  4. Cancel")

        choice = input("\nYour choice (1-4): ").strip()

        if choice == "1":
            ret, _, _ = run_command("git stash")
            if ret == 0:
                print_success("Changes stashed")
            else:
                print_error("Failed to stash changes")
                return False
        elif choice == "2":
            for change in uncommitted:
                print(f"  {change}")
            print()
            retry = input("Continue with merge? (y/n): ").strip().lower()
            if retry not in ['y', 'yes']:
                print_info("Merge cancelled")
                return False
        elif choice == "4":
            print_info("Merge cancelled")
            return False
        # choice == 3 falls through to continue

    # Check for conflict markers - auto-clean if from previous failed merge
    if check_conflict_markers():
        print_warning("[WARN] Conflict markers detected from previous merge - auto-cleaning...")
        logger.info("Auto-cleaning conflict markers from previous failed merge")

        # Abort any ongoing merge/rebase
        run_command("git merge --abort", capture_output=True)
        run_command("git rebase --abort", capture_output=True)

        # Restore conflicted files from HEAD
        returncode, stdout, _ = run_command("git diff --name-only --diff-filter=U", capture_output=True)
        if returncode == 0 and stdout:
            for f in stdout.strip().split('\n'):
                if f.strip():
                    run_command(f'git checkout HEAD -- "{f.strip()}"', capture_output=True)

        # Also restore any files with conflict markers that are just modified (not unmerged)
        returncode, stdout, _ = run_command("git diff --check", capture_output=True)
        if returncode != 0 and stdout:
            conflict_files = set()
            for line in stdout.split('\n'):
                if 'leftover conflict marker' in line:
                    conflict_files.add(line.split(':')[0])
            for f in conflict_files:
                run_command(f'git checkout HEAD -- "{f}"', capture_output=True)
                print_info(f"  [OK] Restored {f} from HEAD")

        # Verify
        if check_conflict_markers():
            print_error("[FAIL] Could not auto-clean all conflict markers")
            print_warning("Please resolve manually:")
            print("  1. git status")
            print("  2. Edit conflicted files")
            print("  3. git add <files> && git commit")
            return False
        else:
            print_success("[OK] Conflict markers cleaned successfully")

    # CRITICAL: Ensure main branch is up to date before merging Claude branches
    current_branch = get_current_branch()
    if current_branch != DEFAULT_BRANCH:
        print_info(f"Switching from '{current_branch}' to '{DEFAULT_BRANCH}' branch...")
        ret, _, _ = run_command(f"git checkout {DEFAULT_BRANCH}")
        if ret != 0:
            print_error(f"Failed to switch to {DEFAULT_BRANCH} branch")
            return False
        print_success(f"Switched to {DEFAULT_BRANCH} branch")

    print_info(f"Ensuring {DEFAULT_BRANCH} branch is up to date with remote...")
    ret, _, stderr = run_command(f"git pull origin {DEFAULT_BRANCH}")
    if ret != 0:
        print_error(f"Failed to pull latest from origin/{DEFAULT_BRANCH}: {stderr}")
        print_warning(f"This might cause merge conflicts due to outdated {DEFAULT_BRANCH} branch")
        retry = input("Continue anyway? (y/n): ").strip().lower()
        if retry not in ['y', 'yes']:
            return False
    else:
        print_success(f"{DEFAULT_BRANCH} branch is up to date")

    print_info("Checking for new Claude branches...")
    claude_branches = get_claude_branches()

    if not claude_branches:
        logger.info("No Claude branches with new commits found.")
        print_info("No Claude branches with new commits found.")
        return False

    logger.info(f"Found {len(claude_branches)} Claude branch(es) to merge")
    print_warning(f"Found {len(claude_branches)} Claude branch(es) with new commits:")
    print()

    for i, branch_info in enumerate(claude_branches, 1):
        print(f"{Colors.BOLD}{i}. {branch_info['name']}{Colors.END}")
        print(f"   {len(branch_info['commits'])} new commit(s):")
        for commit in branch_info['commits'][:3]:
            print(f"     {commit}")
        if len(branch_info['commits']) > 3:
            print(f"     ... and {len(branch_info['commits']) - 3} more")
        print()

    choice = input(f"{Colors.BOLD}Merge Claude branches to {DEFAULT_BRANCH}? (y/n or yes/no):{Colors.END} ").strip().lower()
    logger.info(f"User choice for merge: {choice}")

    if choice not in ['yes', 'y']:
        logger.info("User cancelled merge operation")
        return False

    # CRITICAL: Clean any ongoing merge/rebase state before starting
    clean_merge_state()

    # CRITICAL: Stash local changes to avoid 'would be overwritten by merge' errors
    stash_msg = stash_local_changes()

    # Merge each branch
    for branch_info in claude_branches:
        logger.info(f"Attempting to merge: {branch_info['name']}")
        print_info(f"Merging {branch_info['name']}...")

        # First try fast-forward merge
        returncode, stdout, stderr = run_command(f"git merge {branch_info['full_name']} --ff-only")

        if returncode == 0:
            logger.info(f"Successfully merged {branch_info['name']} (fast-forward)")
            print_success(f"Merged {branch_info['name']} successfully!")
        else:
            # Fast-forward failed - check if it's divergence or other issue
            logger.warning(f"Fast-forward merge failed for {branch_info['name']}: {stderr}")

            # Check for divergence
            ret, ahead, _ = run_command(f"git rev-list --count {DEFAULT_BRANCH}..{branch_info['full_name']}")
            ret2, behind, _ = run_command(f"git rev-list --count {branch_info['full_name']}..{DEFAULT_BRANCH}")

            if ret == 0 and ret2 == 0:
                ahead_count = int(ahead) if ahead else 0
                behind_count = int(behind) if behind else 0

                if ahead_count > 0 and behind_count > 0:
                    print_warning(f"Branches have diverged!")
                    print(f"  {branch_info['name']} is ahead by {ahead_count} commit(s)")
                    print(f"  {DEFAULT_BRANCH} is ahead by {behind_count} commit(s)")
                    print()
                    print("Merge strategies:")
                    print(f"  {Colors.BOLD}1.{Colors.END} Rebase claude branch onto {DEFAULT_BRANCH} (recommended - cleaner history)")
                    print(f"  {Colors.BOLD}2.{Colors.END} Merge with merge commit (preserves full history)")
                    print(f"  {Colors.BOLD}3.{Colors.END} Skip this branch")

                    strategy = input("\nYour choice (1-3): ").strip()
                    logger.info(f"User selected merge strategy: {strategy}")

                    if strategy == "1":
                        # Rebase strategy
                        print_info(f"Rebasing branch onto {DEFAULT_BRANCH}...")
                        temp_branch = f"temp_merge_{branch_info['name'].split('/')[-1]}"

                        # Clean up any existing temp branch first (in case of previous failures)
                        # Check if temp branch exists first
                        ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                        if ret_check == 0:
                            # Branch exists, delete it
                            run_command(f"git branch -D {temp_branch}", capture_output=True)

                        # Checkout the branch locally first
                        run_command(f"git checkout -b {temp_branch} {branch_info['full_name']}")
                        returncode, stdout, stderr = run_command(f"git rebase {DEFAULT_BRANCH}")

                        if returncode == 0:
                            print_success("Rebase successful!")
                            # Now merge the rebased branch
                            run_command(f"git checkout {DEFAULT_BRANCH}")
                            returncode2, _, _ = run_command(f"git merge {temp_branch} --ff-only")

                            if returncode2 == 0:
                                logger.info(f"Successfully merged {branch_info['name']} after rebase")
                                print_success(f"Merged {branch_info['name']} successfully!")
                                # Cleanup temp branch
                                run_command(f"git branch -D {temp_branch}")
                            else:
                                print_error("Merge failed after rebase!")
                                run_command(f"git checkout {DEFAULT_BRANCH}")
                                run_command(f"git branch -D {temp_branch}")
                                return False
                        else:
                            # Rebase failed - check for conflicts or already-merged commits
                            logger.warning(f"Rebase failed: {stderr}")

                            # Check if it's due to already-merged commits or conflicts
                            if 'skipped previously applied commit' in stderr or 'skipped previously applied commit' in stdout:
                                print_warning(f"[WARN] Some commits are already in {DEFAULT_BRANCH} (cherry-picked or merged)")

                            if 'CONFLICT' in stderr or check_conflict_markers():
                                print_error("[WARN] Merge conflicts detected during rebase!")
                                print()
                                print("Options:")
                                print("  1. Abort rebase and try merge strategy instead (recommended)")
                                print("  2. Abort rebase and skip this branch")
                                print("  3. Keep conflict state for manual resolution")

                                conflict_choice = input("\nYour choice (1-3): ").strip()

                                if conflict_choice == "1":
                                    print_info("Aborting rebase and trying merge strategy...")
                                    run_command("git rebase --abort")
                                    run_command(f"git checkout {DEFAULT_BRANCH}")
                                    # Delete temp branch if it exists
                                    ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                                    if ret_check == 0:
                                        run_command(f"git branch -D {temp_branch}", capture_output=True)

                                    # Try merge with commit instead
                                    returncode, _, stderr = run_command(f"git merge {branch_info['full_name']} --no-ff")
                                    if returncode == 0:
                                        logger.info(f"Successfully merged {branch_info['name']} (merge commit)")
                                        print_success(f"Merged {branch_info['name']} successfully using merge strategy!")
                                    else:
                                        # Merge also has conflicts - try auto-resolution
                                        print_warning("Merge conflicts detected, attempting auto-resolution...")
                                        resolved_count, total_conflicts = auto_resolve_add_add_conflicts()
                                        if resolved_count > 0 and resolved_count == total_conflicts:
                                            print_success("[OK] All conflicts auto-resolved!")
                                            ret, _, _ = run_command('git commit --no-edit', capture_output=True)
                                            if ret == 0:
                                                logger.info(f"Successfully merged {branch_info['name']} (auto-resolved)")
                                                print_success(f"Merged {branch_info['name']} successfully!")
                                            else:
                                                print_error("Failed to commit after auto-resolve")
                                                return False
                                        else:
                                            logger.error(f"Merge also failed: {stderr}")
                                            print_error("Auto-resolution failed. Please resolve manually.")
                                            print_info("Or to abort: git merge --abort")
                                            return False
                                elif conflict_choice == "2":
                                    print_warning("Aborting rebase and skipping branch...")
                                    run_command("git rebase --abort")
                                    run_command(f"git checkout {DEFAULT_BRANCH}")
                                    # Delete temp branch if it exists
                                    ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                                    if ret_check == 0:
                                        run_command(f"git branch -D {temp_branch}", capture_output=True)
                                    continue  # Skip to next branch
                                else:
                                    print_warning("Keeping conflict state. Resolve manually:")
                                    print("  1. Fix conflicts in files")
                                    print("  2. git add <resolved-files>")
                                    print("  3. git rebase --continue")
                                    return False
                            else:
                                # Non-conflict rebase failure
                                print_error(f"Rebase failed: {stderr}")
                                print_warning("Aborting rebase...")
                                run_command("git rebase --abort")
                                run_command(f"git checkout {DEFAULT_BRANCH}")
                                # Delete temp branch if it exists
                                ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                                if ret_check == 0:
                                    run_command(f"git branch -D {temp_branch}", capture_output=True)
                                return False

                    elif strategy == "2":
                        # Merge with commit
                        print_info("Merging with merge commit...")
                        returncode, _, stderr = run_command(f"git merge {branch_info['full_name']} --no-ff")
                        if returncode == 0:
                            logger.info(f"Successfully merged {branch_info['name']} (merge commit)")
                            print_success("Merge successful!")
                        else:
                            # Merge has conflicts - try auto-resolution
                            print_warning(f"Merge conflicts detected for {branch_info['name']}")
                            print_info("[AUTO] Attempting to auto-resolve conflicts...")
                            resolved_count, total_conflicts = auto_resolve_add_add_conflicts()

                            if resolved_count > 0 and resolved_count == total_conflicts:
                                print_success("[OK] All conflicts auto-resolved!")
                                ret, _, _ = run_command('git commit --no-edit', capture_output=True)
                                if ret == 0:
                                    logger.info(f"Successfully merged {branch_info['name']} (auto-resolved)")
                                    print_success(f"Merged {branch_info['name']} successfully!")
                                else:
                                    print_error("Failed to commit after auto-resolve")
                                    return False
                            else:
                                logger.error(f"Merge failed: {stderr}")
                                print_error(f"  {total_conflicts - resolved_count}/{total_conflicts} conflict(s) need manual resolution")
                                print_info("Resolve manually, then: git add <files> && git commit")
                                print_info("Or to abort: git merge --abort")
                                return False
                    else:
                        print_warning(f"Skipping {branch_info['name']}")
                        continue
                else:
                    # Not diverged, just can't fast-forward for some reason
                    print_error(f"Cannot fast-forward merge {branch_info['name']}")
                    retry = input("Try merge with commit? (y/n or yes/no): ").strip().lower()
                    logger.info(f"User choice for non-ff merge: {retry}")

                    if retry in ['yes', 'y']:
                        returncode, _, stderr = run_command(f"git merge {branch_info['full_name']} --no-ff")
                        if returncode == 0:
                            logger.info(f"Successfully merged {branch_info['name']} (non-fast-forward)")
                            print_success("Merge successful!")
                        else:
                            logger.error(f"Failed to merge {branch_info['name']}: {stderr}")
                            print_error("Merge failed! Please resolve manually.")
                            return False
                    else:
                        continue

    # Restore stashed changes
    if stash_msg:
        pop_stash(stash_msg)

    logger.info("All Claude branches merged successfully")
    return True

def cleanup_merged_claude_branches():
    """Delete merged Claude branches (local and remote)"""
    print_info("Checking for merged Claude branches...")

    # Get all local claude branches (Windows compatible - no grep)
    returncode, stdout, _ = run_command("git branch")
    local_branches = []
    if returncode == 0 and stdout:
        for line in stdout.split('\n'):
            branch = line.strip().replace('* ', '')
            if branch and 'claude/' in branch:
                local_branches.append(branch)

    # Get all remote claude branches (Windows compatible - no grep)
    returncode, stdout, _ = run_command("git branch -r")
    remote_branches = []
    if returncode == 0 and stdout:
        for line in stdout.split('\n'):
            branch = line.strip()
            if branch and 'origin/claude/' in branch:
                remote_branches.append(branch.replace('origin/', ''))

    total_branches = len(local_branches) + len(remote_branches)

    if total_branches == 0:
        print_success("No Claude branches to cleanup!")
        return True

    print_warning(f"Found {len(local_branches)} local and {len(remote_branches)} remote Claude branch(es):")
    print()

    if local_branches:
        print(f"{Colors.BOLD}Local branches:{Colors.END}")
        for branch in local_branches[:10]:
            print(f"  • {branch}")
        if len(local_branches) > 10:
            print(f"  ... and {len(local_branches) - 10} more")
        print()

    if remote_branches:
        print(f"{Colors.BOLD}Remote branches:{Colors.END}")
        for branch in remote_branches[:10]:
            print(f"  • {branch}")
        if len(remote_branches) > 10:
            print(f"  ... and {len(remote_branches) - 10} more")
        print()

    choice = input(f"{Colors.BOLD}Delete all Claude branches? (y/n or yes/no):{Colors.END} ").strip().lower()

    if choice not in ['yes', 'y']:
        print_warning("Cleanup cancelled")
        return False

    # Delete local branches
    if local_branches:
        print_info("Deleting local branches...")
        for branch in local_branches:
            returncode, _, stderr = run_command(f"git branch -D {branch}")
            if returncode == 0:
                print_success(f"Deleted local: {branch}")
            else:
                print_error(f"Failed to delete: {branch}")
                if stderr:
                    print(f"    {stderr}")

    # Delete remote branches
    if remote_branches:
        print_info("Deleting remote branches...")
        # Delete all at once for efficiency
        branches_str = ' '.join(remote_branches)
        returncode, stdout, stderr = run_command(f"git push origin --delete {branches_str}")
        if returncode == 0:
            print_success(f"Deleted {len(remote_branches)} remote branch(es)")
        else:
            print_error("Failed to delete remote branches")
            if stderr:
                print(stderr)

    # Prune remote references
    print_info("Pruning remote references...")
    run_command("git fetch --prune")

    print_success("Cleanup completed!")
    return True

# ========== VERIFICATION FUNCTIONS ==========

def check_file_contains(filepath, search_string):
    """Check if file contains a specific string"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return search_string in content
    except Exception:
        return False

def check_multiline_pattern(filepath, lines_to_find):
    """Check if file contains multiple consecutive lines"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            search_pattern = '\n'.join(lines_to_find)
            content_normalized = content.replace('\r\n', '\n')
            return search_pattern in content_normalized
    except Exception:
        return False

def print_check(check_name, passed, details=""):
    """Print verification check result"""
    if passed:
        print(f"  {Colors.GREEN}{Colors.CHECK}{Colors.END} {check_name}")
        if details:
            print(f"    {Colors.CYAN}{details}{Colors.END}")
    else:
        print(f"  {Colors.RED}{Colors.CROSS}{Colors.END} {check_name}")
        if details:
            print(f"    {Colors.YELLOW}{details}{Colors.END}")
    return passed

def verify_all_changes():
    """Verify that all Claude branch changes are present"""
    clear_screen()
    print_header("Verification - Claude Branches Changes")

    total_checks = 0
    passed_checks = 0

    # Branch 1: Theme Fix
    print(f"{Colors.BOLD}Branch 1: Theme Switching Fix{Colors.END}")
    print(f"{Colors.YELLOW}Commit: bb423de{Colors.END}\n")

    total_checks += 1
    if print_check(
        "Theme initTheme() function exists",
        check_file_contains('app/templates/components/scripts.html', 'initTheme()'),
        "Loads theme from localStorage on startup"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "Theme applyTheme() function exists",
        check_file_contains('app/templates/components/scripts.html', 'applyTheme(theme)'),
        "Applies theme to document.body"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "localStorage.setItem for theme",
        check_file_contains('app/templates/components/scripts.html', "localStorage.setItem('theme', theme)"),
        "Theme is saved to localStorage"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "init() calls initTheme()",
        check_file_contains('app/templates/components/scripts.html', 'this.initTheme()'),
        "Theme loads on application startup"
    ):
        passed_checks += 1

    print()

    # Branch 2: Safe Git Pull v2.1
    print(f"{Colors.BOLD}Branch 2: Safe Git Pull v2.1{Colors.END}")
    print(f"{Colors.YELLOW}Commit: afb3be7{Colors.END}\n")

    total_checks += 1
    if print_check(
        "get_claude_branches() function",
        check_file_contains('safe-git-pull.py', 'def get_claude_branches()'),
        "Detects remote claude/* branches"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "check_and_merge_claude_branches() function",
        check_file_contains('safe-git-pull.py', 'def check_and_merge_claude_branches()'),
        "Merges Claude branches to default branch"
    ):
        passed_checks += 1

    print()

    # Branch 3: Safe Git Pull v2.2
    print(f"{Colors.BOLD}Branch 3: Safe Git Pull v2.2{Colors.END}")
    print(f"{Colors.YELLOW}Commit: b717e1a{Colors.END}\n")

    total_checks += 1
    if print_check(
        "interactive_menu() has while True loop",
        check_file_contains('safe-git-pull.py', 'while True:'),
        "Menu loops after viewing information"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "Press Enter to continue prompts",
        check_file_contains('safe-git-pull.py', 'Press Enter to continue'),
        "User can return to menu after viewing"
    ):
        passed_checks += 1

    print()

    # Branch 5: PSE Scanner Depth
    print(f"{Colors.BOLD}Branch 5: PSE Scanner 5-level Depth{Colors.END}")
    print(f"{Colors.YELLOW}Commit: caa14e5{Colors.END}\n")

    total_checks += 1
    if print_check(
        "PSE scanner searches 5 levels deep",
        check_file_contains('app/scanners/SAP/scan_pse.py', '*/*/*/*/SEC'),
        "Pattern: */*/*/*/SEC (level 4)"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "PSE scanner level 5 pattern",
        check_file_contains('app/scanners/SAP/scan_pse.py', '*/*/*/*/*/SEC'),
        "Pattern: */*/*/*/*/SEC (level 5)"
    ):
        passed_checks += 1

    print()

    # Branch 6: Scanner Progress Fix
    print(f"{Colors.BOLD}Branch 6: Scanner Progress Race Fix{Colors.END}")
    print(f"{Colors.YELLOW}Commit: 55bb567{Colors.END}\n")

    total_checks += 1
    if print_check(
        "Scanner progress comments present",
        check_file_contains('app/main.py', '# NOW mark as completed'),
        "Progress markers after DB commits"
    ):
        passed_checks += 1

    total_checks += 1
    if print_check(
        "PSE scanner progress timing",
        check_multiline_pattern('app/main.py', [
            "        if session:",
            "            session.status = 'completed'",
            "            session.certificates_found = certs_found"
        ]),
        "DB commit before progress=100"
    ):
        passed_checks += 1

    print()

    # Summary
    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}")
    print(f"{Colors.BOLD}Summary:{Colors.END}\n")

    percentage = (passed_checks / total_checks * 100) if total_checks > 0 else 0

    if passed_checks == total_checks:
        print(f"  {Colors.GREEN}{Colors.BOLD}{Colors.CHECK} ALL CHECKS PASSED!{Colors.END}")
        print(f"  {Colors.GREEN}{passed_checks}/{total_checks} checks successful ({percentage:.0f}%){Colors.END}\n")
        print(f"  {Colors.CYAN}All Claude branch changes are present in your repository!{Colors.END}")
    elif passed_checks > total_checks * 0.8:
        print(f"  {Colors.YELLOW}{Colors.BOLD}{Colors.WARNING_SYMBOL} MOSTLY COMPLETE{Colors.END}")
        print(f"  {Colors.YELLOW}{passed_checks}/{total_checks} checks passed ({percentage:.0f}%){Colors.END}\n")
        print(f"  {Colors.YELLOW}Most changes are present. Review failed checks above.{Colors.END}")
    else:
        print(f"  {Colors.RED}{Colors.BOLD}{Colors.CROSS} MISSING CHANGES{Colors.END}")
        print(f"  {Colors.RED}{passed_checks}/{total_checks} checks passed ({percentage:.0f}%){Colors.END}\n")
        print(f"  {Colors.RED}Several changes are missing. Please merge Claude branches.{Colors.END}")

    print(f"{Colors.BOLD}{'=' * 70}{Colors.END}\n")

    if passed_checks < total_checks:
        print(f"{Colors.YELLOW}{Colors.BOLD}Recommended Actions:{Colors.END}\n")
        print("1. Merge missing branches:")
        print("   python safe-git-pull.py --merge-claude")
        print()
        print("2. Or use the interactive menu (option 4)")
        print()

    return passed_checks == total_checks

# ========== GIT OPERATIONS ==========

def do_pull(branch, uncommitted, new_commits):
    """Perform pull operation"""
    # Check for conflict markers first
    if check_conflict_markers():
        print_error("[WARN] Unresolved conflict markers detected!")
        print_warning("Your repository has unresolved merge conflicts.")
        print()
        print("Options:")
        print("  1. Abort current merge/rebase")
        print("  2. Show conflicted files")
        print("  3. Continue anyway (advanced)")
        print("  4. Cancel")

        choice = input("\nYour choice (1-4): ").strip()

        if choice == "1":
            # Try to abort any ongoing operation
            run_command("git merge --abort", capture_output=True)
            run_command("git rebase --abort", capture_output=True)
            print_success("Aborted ongoing operation")
            return 0
        elif choice == "2":
            run_command("git diff --name-only --diff-filter=U", capture_output=False)
            print_info("\nResolve conflicts manually, then run this script again")
            return 1
        elif choice == "4":
            print_warning("Pull cancelled")
            return 0

    if not new_commits:
        print_success("Already up to date!")
        return 0

    print(f"\n{Colors.GREEN}New commits to pull:{Colors.END}")
    for commit in new_commits[:5]:
        print(f"  {commit}")
    if len(new_commits) > 5:
        print(f"  ... and {len(new_commits) - 5} more")

    if uncommitted:
        print_warning(f"{len(uncommitted)} uncommitted change(s) detected")
        stash = input("Stash changes before pull? (y/n or yes/no): ").strip().lower()
        if stash in ['yes', 'y']:
            returncode, _, _ = run_command("git stash")
            if returncode == 0:
                print_success("Changes stashed")
            else:
                print_error("Failed to stash changes")
                return 1

    print_info("Pulling changes...")
    returncode, stdout, stderr = run_command(f"git pull origin {branch}", capture_output=True)

    if returncode == 0:
        print_success("Pull completed successfully!")
        # Check if there are conflicts after pull
        if check_conflict_markers():
            print_warning("[WARN] Merge conflicts detected after pull!")
            print_info("Use 'git status' to see conflicted files")
            print_info("After resolving conflicts:")
            print("  1. git add <resolved-files>")
            print("  2. git commit")
            return 1

        if uncommitted:
            apply = input("Apply stashed changes? (y/n or yes/no): ").strip().lower()
            if apply in ['yes', 'y']:
                ret, _, stderr = run_command("git stash pop")
                if ret != 0:
                    print_error("Failed to apply stashed changes")
                    print_warning("Your changes are still in stash. Use 'git stash list' to see them")
                    if 'CONFLICT' in stderr:
                        print_warning("Stash conflicts with current state")
                        print_info("Resolve manually or use 'git stash drop' to discard")
                else:
                    print_success("Stashed changes applied")
        return 0
    else:
        print_error("Pull failed!")
        logger.error(f"Pull error: {stderr}")

        # Check for common error patterns
        if 'CONFLICT' in stderr:
            print_warning("[WARN] Merge conflict detected!")
            print_info("Resolve conflicts manually:")
            print("  1. Edit conflicted files")
            print("  2. git add <resolved-files>")
            print("  3. git commit")
        elif 'diverged' in stderr.lower():
            print_warning("[WARN] Branches have diverged!")
            print_info("Use option to handle diverged branches or run:")
            print("  git pull --rebase origin " + branch)
        elif 'Permission denied' in stderr:
            print_error("[WARN] Permission denied - check your SSH key or credentials")
        elif 'Could not resolve host' in stderr:
            print_error("[WARN] Network error - check your internet connection")

        return 1

def do_push(branch, uncommitted, unpushed):
    """Perform push operation"""
    # If there are uncommitted changes but no unpushed commits, offer to commit first
    if uncommitted and not unpushed:
        print_warning(f"{len(uncommitted)} uncommitted change(s)")
        print_info("No commits to push yet.")
        commit = input("Create a commit with these changes? (y/n or yes/no): ").strip().lower()
        if commit in ['yes', 'y']:
            # Show changes
            print(f"\n{Colors.YELLOW}Files to commit:{Colors.END}")
            for change in uncommitted[:10]:
                print(f"  {change}")
            if len(uncommitted) > 10:
                print(f"  ... and {len(uncommitted) - 10} more")

            msg = input("\nCommit message: ").strip()
            if not msg:
                print_warning("Commit cancelled - no message provided")
                return 0

            run_command("git add .")
            run_command(f'git commit -m "{msg}"')
            print_success("Changes committed")

            # Refresh unpushed commits list
            unpushed = check_unpushed_commits(branch)
        else:
            print_warning("Push cancelled")
            return 0

    if not unpushed:
        print_success("Nothing to push!")
        return 0

    if uncommitted:
        print_warning(f"{len(uncommitted)} uncommitted change(s)")
        commit = input("Commit changes before push? (y/n or yes/no): ").strip().lower()
        if commit in ['yes', 'y']:
            msg = input("Commit message: ").strip()
            run_command("git add .")
            run_command(f'git commit -m "{msg}"')
            print_success("Changes committed")

    print(f"\n{Colors.YELLOW}Commits to push:{Colors.END}")
    for commit in unpushed[:5]:
        print(f"  {commit}")
    if len(unpushed) > 5:
        print(f"  ... and {len(unpushed) - 5} more")

    confirm = input("\nProceed with push? (y/n or yes/no): ").strip().lower()
    if confirm not in ['yes', 'y']:
        print_warning("Push cancelled")
        return 0

    print_info("Pushing changes...")
    returncode, _, _ = run_command(f"git push origin {branch}", capture_output=False)

    if returncode == 0:
        print_success("Push completed successfully!")
        return 0
    else:
        print_error("Push failed!")
        return 1

def do_sync(branch, uncommitted, unpushed, new_commits):
    """Perform sync (pull + push) operation"""
    # First pull
    if new_commits:
        result = do_pull(branch, uncommitted, new_commits)
        if result != 0:
            return result
        # Refresh unpushed commits after pull
        unpushed = check_unpushed_commits(branch)

    # Then push
    if unpushed:
        return do_push(branch, [], unpushed)

    print_success("Repository is in sync!")
    return 0

def do_stash():
    """Stash uncommitted changes"""
    # Check if there's a merge/rebase in progress
    operation_type, operation_msg = check_merge_in_progress()

    if operation_type:
        print_error(f"[FAIL] Cannot stash during {operation_type}!")
        print(f"   {operation_msg}")
        print()
        print("You need to resolve this first:")
        print()

        if operation_type == "merge":
            print("Merge Resolution Options:")
            print(f"  {Colors.BOLD}1.{Colors.END} Abort merge (git merge --abort)")
            print(f"     {Colors.YELLOW}WARNING: This will discard the merge attempt{Colors.END}")
            print()
            print(f"  {Colors.BOLD}2.{Colors.END} Show conflicted files (git status)")
            print()
            print(f"  {Colors.BOLD}3.{Colors.END} Get resolution instructions")
            print()
            print(f"  {Colors.BOLD}4.{Colors.END} Cancel and resolve manually")

            choice = input("\nYour choice (1-4): ").strip()

            if choice == "1":
                print_warning("Aborting merge...")
                ret, _, _ = run_command("git merge --abort")
                if ret == 0:
                    print_success("Merge aborted. Working tree is clean.")
                    return 0
                else:
                    print_error("Failed to abort merge")
                    return 1

            elif choice == "2":
                run_command("git status")
                return 1

            elif choice == "3":
                print()
                print("To resolve merge conflicts:")
                print("  1. Run: git status")
                print("  2. Edit conflicted files (look for <<<<<<< markers)")
                print("  3. Remove conflict markers and keep desired code")
                print("  4. Run: git add <resolved-files>")
                print("  5. Run: git commit")
                print()
                print("Or to abort: git merge --abort")
                return 1

            else:
                print_info("Cancelled")
                return 1

        elif operation_type == "rebase":
            print("Rebase Resolution Options:")
            print(f"  {Colors.BOLD}1.{Colors.END} Abort rebase (git rebase --abort)")
            print(f"     {Colors.YELLOW}WARNING: This will discard the rebase attempt{Colors.END}")
            print()
            print(f"  {Colors.BOLD}2.{Colors.END} Show conflicted files")
            print()
            print(f"  {Colors.BOLD}3.{Colors.END} Get resolution instructions")
            print()
            print(f"  {Colors.BOLD}4.{Colors.END} Cancel and resolve manually")

            choice = input("\nYour choice (1-4): ").strip()

            if choice == "1":
                print_warning("Aborting rebase...")
                ret, _, _ = run_command("git rebase --abort")
                if ret == 0:
                    print_success("Rebase aborted. Working tree is clean.")
                    return 0
                else:
                    print_error("Failed to abort rebase")
                    return 1

            elif choice == "2":
                run_command("git status")
                return 1

            elif choice == "3":
                print()
                print("To resolve rebase conflicts:")
                print("  1. Run: git status")
                print("  2. Edit conflicted files")
                print("  3. Run: git add <resolved-files>")
                print("  4. Run: git rebase --continue")
                print()
                print("Or to abort: git rebase --abort")
                return 1

            else:
                print_info("Cancelled")
                return 1

        return 1

    # No merge in progress, proceed with normal stash
    changes = check_git_status()
    if not changes:
        print_info("No changes to stash")
        return 0

    print(f"{Colors.YELLOW}Changes to stash:{Colors.END}")
    for change in changes[:10]:
        print(f"  {change}")
    if len(changes) > 10:
        print(f"  ... and {len(changes) - 10} more")

    msg = input("\nStash message (optional): ").strip()
    if msg:
        returncode, _, _ = run_command(f'git stash push -m "{msg}"')
    else:
        returncode, _, _ = run_command("git stash")

    if returncode == 0:
        print_success("Changes stashed successfully!")
        return 0
    else:
        print_error("Stash failed!")
        return 1

def show_uncommitted_changes():
    """Show uncommitted changes"""
    changes = check_git_status()
    if not changes:
        print_info("No uncommitted changes")
    else:
        print(f"\n{Colors.YELLOW}Uncommitted changes ({len(changes)}):{Colors.END}")
        for change in changes:
            print(f"  {change}")

def show_unpushed_commits(branch):
    """Show unpushed commits"""
    commits = check_unpushed_commits(branch)
    if not commits:
        print_info("No unpushed commits")
    else:
        print(f"\n{Colors.YELLOW}Unpushed commits ({len(commits)}):{Colors.END}")
        for commit in commits:
            print(f"  {commit}")

def handle_diverged_branches(branch, local_ahead, remote_ahead):
    """Handle diverged branches with smart suggestions"""
    print_warning("[WARN] Branches have diverged!")
    print(f"  Local is ahead by {local_ahead} commit(s)")
    print(f"  Remote is ahead by {remote_ahead} commit(s)")
    print()

    # Show what commits are different
    print(f"{Colors.YELLOW}Local commits not on remote:{Colors.END}")
    ret, local_commits, _ = run_command(f"git log origin/{branch}..HEAD --oneline")
    if ret == 0 and local_commits:
        local_commits_list = local_commits.split('\n')
        for commit in local_commits_list[:3]:
            print(f"  {commit}")
        if len(local_commits_list) > 3:
            print(f"  ... and {len(local_commits_list) - 3} more")

    print()
    print(f"{Colors.YELLOW}Remote commits not in local:{Colors.END}")
    ret, remote_commits, _ = run_command(f"git log HEAD..origin/{branch} --oneline")
    if ret == 0 and remote_commits:
        remote_commits_list = remote_commits.split('\n')
        for commit in remote_commits_list[:3]:
            print(f"  {commit}")
        if len(remote_commits_list) > 3:
            print(f"  ... and {len(remote_commits_list) - 3} more")

    print()
    print("Resolution Options:")
    print(f"  {Colors.BOLD}1.{Colors.END} Pull with rebase (recommended - cleaner history)")
    print(f"     Your local commits will be replayed on top of remote")
    print()
    print(f"  {Colors.BOLD}2.{Colors.END} Pull with merge commit (safe - preserves both histories)")
    print(f"     Creates a merge commit combining both branches")
    print()
    print(f"  {Colors.BOLD}3.{Colors.END} Force push ([WARN] DANGEROUS - overwrites remote)")
    print(f"     {Colors.RED}WARNING: This will DELETE remote commits!{Colors.END}")
    print()
    print(f"  {Colors.BOLD}4.{Colors.END} Show detailed diff")
    print(f"     Compare local and remote changes in detail")
    print()
    print(f"  {Colors.BOLD}5.{Colors.END} Create backup branch and reset")
    print(f"     Saves current state to backup branch, then resets to remote")
    print()
    print(f"  {Colors.BOLD}6.{Colors.END} Cancel")

    choice = input(f"\n{Colors.BOLD}Your choice (1-6):{Colors.END} ").strip()

    if choice == "1":
        print_info("Rebasing local commits onto remote...")
        returncode, stdout, stderr = run_command(f"git pull origin {branch} --rebase", capture_output=True)

        if returncode == 0:
            print_success("Rebase successful!")
            return True
        else:
            print_error("Rebase failed!")
            logger.error(f"Rebase error: {stderr}")

            # Check for already-merged commits
            if 'skipped previously applied commit' in stderr or 'skipped previously applied commit' in stdout:
                print_warning("[WARN] Some commits were already merged (cherry-picked)")

            if 'CONFLICT' in stderr or check_conflict_markers():
                print_warning("[WARN] Conflicts detected during rebase")
                print()
                print("Options:")
                print("  1. Abort rebase and try merge strategy instead")
                print("  2. Continue manually resolving conflicts")
                print("  3. Abort rebase and cancel")

                resolve_choice = input("\nYour choice (1-3): ").strip()

                if resolve_choice == "1":
                    print_info("Aborting rebase and trying merge strategy...")
                    run_command("git rebase --abort")

                    # Try merge instead
                    returncode, _, stderr = run_command(f"git pull origin {branch}", capture_output=True)
                    if returncode == 0:
                        print_success("Merge successful!")
                        return True
                    else:
                        print_error("Merge also failed!")
                        logger.error(f"Merge error: {stderr}")
                        return False
                elif resolve_choice == "2":
                    print()
                    print("To resolve conflicts:")
                    print("  1. Edit conflicted files (git status shows them)")
                    print("  2. git add <resolved-files>")
                    print("  3. git rebase --continue")
                    print()
                    print("Or to abort:")
                    print("  git rebase --abort")
                    return False
                else:
                    print_info("Aborting rebase...")
                    run_command("git rebase --abort")
                    return False
            else:
                # Non-conflict rebase error
                print_warning("Rebase failed without conflicts. Trying merge strategy...")
                run_command("git rebase --abort 2>/dev/null", capture_output=True)

                returncode, _, stderr = run_command(f"git pull origin {branch}", capture_output=True)
                if returncode == 0:
                    print_success("Merge successful!")
                    return True
                else:
                    print_error("Both rebase and merge failed!")
                    return False

    elif choice == "2":
        print_info("Merging with merge commit...")
        returncode, stdout, stderr = run_command(f"git pull origin {branch}", capture_output=True)

        if returncode == 0:
            print_success("Merge successful!")
            return True
        else:
            print_error("Merge failed!")
            logger.error(f"Merge error: {stderr}")

            if 'CONFLICT' in stderr:
                print_warning("[WARN] Conflicts detected during merge")
                print()
                print("To resolve:")
                print("  1. Edit conflicted files (git status shows them)")
                print("  2. git add <resolved-files>")
                print("  3. git commit")
                print()
                print("Or to abort:")
                print("  git merge --abort")
            return False

    elif choice == "3":
        print()
        print(f"{Colors.RED}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}[WARN] WARNING: FORCE PUSH IS DANGEROUS!{Colors.END}")
        print(f"{Colors.RED}{Colors.BOLD}{'=' * 70}{Colors.END}")
        print()
        print(f"{Colors.RED}This will PERMANENTLY DELETE {remote_ahead} commit(s) from remote!{Colors.END}")
        print(f"{Colors.RED}Other team members may lose work!{Colors.END}")
        print()
        print("Are you absolutely sure? Type 'yes I am sure' to continue:")
        confirm = input("> ").strip()

        if confirm == "yes I am sure":
            print_warning("Force pushing...")
            returncode, stdout, stderr = run_command(f"git push origin {branch} --force-with-lease", capture_output=True)

            if returncode == 0:
                print_success("Force push successful")
                print_warning("Remote commits were overwritten!")
                return True
            else:
                print_error("Force push failed!")
                logger.error(f"Force push error: {stderr}")

                if 'stale info' in stderr.lower():
                    print_warning("Remote was updated since last fetch")
                    print_info("Someone else pushed changes. Fetch and try again.")
                return False
        else:
            print_info("Force push cancelled (smart choice!)")
            return False

    elif choice == "4":
        print_info("Showing detailed diff between local and remote...")
        print()
        print(f"{Colors.CYAN}=== Changes in local (not on remote) ==={Colors.END}")
        run_command(f"git diff origin/{branch}..HEAD", capture_output=False)
        print()
        print(f"{Colors.CYAN}=== Changes on remote (not in local) ==={Colors.END}")
        run_command(f"git diff HEAD..origin/{branch}", capture_output=False)
        print()
        input("Press Enter to return to options...")
        return handle_diverged_branches(branch, local_ahead, remote_ahead)  # Recurse to show menu again

    elif choice == "5":
        backup_name = f"backup_{branch}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print_info(f"Creating backup branch: {backup_name}")

        returncode, _, _ = run_command(f"git branch {backup_name}")
        if returncode == 0:
            print_success(f"Backup created: {backup_name}")
            print_info(f"Resetting {branch} to match remote...")

            returncode2, _, _ = run_command(f"git reset --hard origin/{branch}")
            if returncode2 == 0:
                print_success(f"Branch {branch} reset to remote")
                print_info(f"Your old commits are saved in: {backup_name}")
                return True
            else:
                print_error("Reset failed!")
                return False
        else:
            print_error("Failed to create backup branch")
            return False

    elif choice == "6":
        print_info("Cancelled")
        return False

    else:
        print_warning("Invalid choice")
        return False

def do_auto_workflow(branch, use_rebase=False):
    """
    Automatic workflow: Merge Claude branches → Sync → Cleanup
    Runs without user prompts (auto-accepts all confirmations)

    Args:
        branch: Current branch name
        use_rebase: If True, rebase claude branches before merging (cleaner history)
    """
    print_header("Automatic Workflow - Merge, Sync & Cleanup")

    if use_rebase:
        print_info(f"Using rebase strategy for cleaner history...")
    else:
        print_info(f"Using default merge strategy...")

    # Pre-check: Clean up any leftover merge/rebase state and conflict markers
    clean_merge_state()
    if check_conflict_markers():
        print_warning("[AUTO] Cleaning conflict markers from previous failed merge...")
        # Restore all conflicted files from HEAD
        returncode, stdout, _ = run_command("git diff --check", capture_output=True)
        if returncode != 0 and stdout:
            conflict_files = set()
            for line in stdout.split('\n'):
                if 'leftover conflict marker' in line:
                    conflict_files.add(line.split(':')[0])
            for f in conflict_files:
                run_command(f'git checkout HEAD -- "{f}"', capture_output=True)
                print_info(f"  [OK] Restored {f} from HEAD")
        if not check_conflict_markers():
            print_success("[OK] Conflict markers cleaned")
        else:
            print_error("[FAIL] Could not clean conflict markers. Please resolve manually.")
            return

    # Step 1: Merge Claude branches to default branch
    print_info(f"Step 1/3: Merging Claude branches to {DEFAULT_BRANCH}...")
    print()

    claude_branches = get_claude_branches()

    if not claude_branches:
        print_info("No Claude branches with new commits found.")
    else:
        print_success(f"Found {len(claude_branches)} Claude branch(es) with new commits")

        # CRITICAL: Stash local changes before any merge to avoid
        # "Your local changes would be overwritten by merge" errors
        stash_msg = stash_local_changes()

        # Auto-merge each branch
        for i, branch_info in enumerate(claude_branches, 1):
            print_info(f"[{i}/{len(claude_branches)}] Merging {branch_info['name']}...")

            if use_rebase:
                # Rebase strategy for cleaner history
                temp_branch = f"temp_merge_{branch_info['name'].split('/')[-1]}"

                # CRITICAL: Clean any ongoing merge/rebase state before proceeding
                clean_merge_state()

                # Clean up any existing temp branch first (in case of previous failures)
                # Check if temp branch exists first
                ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                if ret_check == 0:
                    # Branch exists, delete it
                    run_command(f"git branch -D {temp_branch}", capture_output=True)

                # Checkout the branch locally
                returncode, _, stderr = run_command(f"git checkout -b {temp_branch} {branch_info['full_name']}")
                if returncode != 0:
                    print_error(f"[FAIL] Failed to checkout {branch_info['name']}: {stderr}")
                    return False

                # Rebase onto default branch
                print_info(f"  Rebasing {branch_info['name']} onto {DEFAULT_BRANCH}...")
                returncode, stdout, stderr = run_command(f"git rebase {DEFAULT_BRANCH}")

                if returncode == 0:
                    # Rebase successful, now merge back to main
                    run_command(f"git checkout {DEFAULT_BRANCH}")
                    returncode2, _, _ = run_command(f"git merge {temp_branch} --ff-only")

                    if returncode2 == 0:
                        print_success(f"[OK] Merged {branch_info['name']} (rebased, fast-forward)")
                        # Cleanup temp branch
                        run_command(f"git branch -D {temp_branch}")
                    else:
                        print_error(f"[FAIL] Fast-forward merge failed after rebase")
                        run_command(f"git checkout {DEFAULT_BRANCH}")
                        run_command(f"git branch -D {temp_branch}")
                        return False
                else:
                    # Rebase failed - try merge strategy as fallback
                    logger.warning(f"Rebase failed for {branch_info['name']}: {stderr}")

                    # Check if it's due to already-merged commits
                    if 'skipped previously applied commit' in stderr or 'skipped previously applied commit' in stdout:
                        print_warning(f"  [WARN] Some commits already in {DEFAULT_BRANCH} (cherry-picked)")

                    # Check for conflicts
                    has_conflicts = 'CONFLICT' in stderr or check_conflict_markers()

                    if has_conflicts:
                        print_warning("  [WARN] Merge conflicts detected - trying merge strategy instead...")
                    else:
                        print_warning("  [WARN] Rebase failed - trying merge strategy instead...")

                    # Abort rebase and cleanup
                    run_command("git rebase --abort")
                    run_command(f"git checkout {DEFAULT_BRANCH}")
                    # Delete temp branch if it exists
                    ret_check, _, _ = run_command(f"git rev-parse --verify {temp_branch}", capture_output=True)
                    if ret_check == 0:
                        run_command(f"git branch -D {temp_branch}", capture_output=True)

                    # Fallback to merge strategy
                    # CRITICAL: Clean any ongoing merge state before trying merge
                    clean_merge_state()

                    # Local changes already stashed at the top of the merge loop

                    print_info(f"  Attempting merge with commit for {branch_info['name']}...")
                    returncode, _, stderr = run_command(f"git merge {branch_info['full_name']} --no-ff")

                    if returncode == 0:
                        print_success(f"[OK] Merged {branch_info['name']} (merge commit - fallback)")
                    else:
                        # Merge failed - try auto-resolution
                        print_warning(f"[WARNING] Merge conflicts detected for {branch_info['name']}")
                        print_info("[AUTO] Attempting to auto-resolve conflicts...")

                        resolved_count, total_conflicts = auto_resolve_add_add_conflicts()

                        if resolved_count > 0 and resolved_count == total_conflicts:
                            # All conflicts resolved - complete the merge
                            print_success("[OK] All conflicts auto-resolved!")
                            print_info("[INFO] Completing merge...")

                            # Commit the merge
                            returncode, _, commit_err = run_command(
                                f'git commit --no-edit',
                                capture_output=True
                            )

                            if returncode == 0:
                                print_success(f"[OK] Merged {branch_info['name']} (auto-resolved conflicts)")
                            else:
                                print_error(f"[FAIL] Failed to commit merge: {commit_err}")
                                print_warning("Aborting automatic workflow")
                                return False
                        else:
                            # Some conflicts remain unresolved
                            print_error(f"[FAIL] Merge failed for {branch_info['name']}")
                            print_error(f"  {total_conflicts - resolved_count}/{total_conflicts} conflict(s) require manual resolution")
                            print_warning("Aborting automatic workflow due to unresolved conflicts")
                            print_info("Please resolve conflicts manually:")
                            print("  1. git status (see conflicted files)")
                            print("  2. Edit and resolve conflicts")
                            print("  3. git add <resolved-files>")
                            print("  4. git commit")
                            return False
            else:
                # Default strategy: Try fast-forward first, then merge commit
                # CRITICAL: Clean any ongoing merge/rebase state before proceeding
                clean_merge_state()

                # Local changes already stashed at the top of the merge loop

                # Try fast-forward merge first
                returncode, stdout, stderr = run_command(f"git merge {branch_info['full_name']} --ff-only")

                if returncode == 0:
                    print_success(f"[OK] Merged {branch_info['name']} (fast-forward)")
                else:
                    # Try merge with commit
                    print_warning("  Fast-forward not possible, trying merge commit...")
                    returncode2, _, stderr2 = run_command(f"git merge {branch_info['full_name']} --no-ff")

                    if returncode2 == 0:
                        print_success(f"[OK] Merged {branch_info['name']} (merge commit)")
                    else:
                        # Merge failed - try auto-resolution
                        print_warning(f"[WARNING] Merge conflicts detected for {branch_info['name']}")
                        print_info("[AUTO] Attempting to auto-resolve conflicts...")

                        resolved_count, total_conflicts = auto_resolve_add_add_conflicts()

                        if resolved_count > 0 and resolved_count == total_conflicts:
                            # All conflicts resolved - complete the merge
                            print_success("[OK] All conflicts auto-resolved!")
                            print_info("[INFO] Completing merge...")

                            # Commit the merge
                            returncode, _, commit_err = run_command(
                                f'git commit --no-edit',
                                capture_output=True
                            )

                            if returncode == 0:
                                print_success(f"[OK] Merged {branch_info['name']} (auto-resolved conflicts)")
                            else:
                                print_error(f"[FAIL] Failed to commit merge: {commit_err}")
                                print_warning("Aborting automatic workflow")
                                return False
                        else:
                            # Some conflicts remain unresolved
                            print_error(f"[FAIL] Failed to merge {branch_info['name']}")
                            print_error(f"  {total_conflicts - resolved_count}/{total_conflicts} conflict(s) require manual resolution")
                            print_warning("Aborting automatic workflow due to unresolved conflicts")
                            print_info("Please resolve manually and try again")
                            return False

        print_success("Step 1/3: All Claude branches merged!")

        # Restore stashed changes (if any)
        if stash_msg:
            pop_stash(stash_msg)

    print()

    # Step 2: Sync (pull + push)
    print_info("Step 2/3: Syncing with remote (pull + push)...")
    print()

    # Refresh state after merge
    uncommitted = check_git_status()
    unpushed = check_unpushed_commits(branch)
    new_commits = get_new_commits(branch)

    # Pull if there are new commits
    if new_commits:
        print_info(f"Pulling {len(new_commits)} new commit(s)...")
        returncode, _, _ = run_command(f"git pull origin {branch}")

        if returncode != 0:
            print_error("Pull failed! Aborting automatic workflow")
            return False

        print_success("[OK] Pulled successfully")

        # Refresh unpushed after pull
        unpushed = check_unpushed_commits(branch)
    else:
        print_success("Already up to date with remote")

    # Push if there are unpushed commits
    if unpushed:
        print_info(f"Pushing {len(unpushed)} commit(s)...")
        returncode, _, _ = run_command(f"git push origin {branch}")

        if returncode != 0:
            print_error("Push failed! Aborting automatic workflow")
            return False

        print_success("[OK] Pushed successfully")
    else:
        print_success("Nothing to push")

    print_success("Step 2/3: Repository synced!")
    print()

    # Step 3: Cleanup merged Claude branches
    print_info("Step 3/3: Cleaning up merged Claude branches...")
    print()

    # Get all local claude branches
    returncode, stdout, _ = run_command("git branch")
    local_branches = []
    if returncode == 0 and stdout:
        for line in stdout.split('\n'):
            branch_name = line.strip().replace('* ', '')
            if branch_name and 'claude/' in branch_name:
                local_branches.append(branch_name)

    # Get all remote claude branches
    returncode, stdout, _ = run_command("git branch -r")
    remote_branches = []
    if returncode == 0 and stdout:
        for line in stdout.split('\n'):
            branch_name = line.strip()
            if branch_name and 'origin/claude/' in branch_name:
                remote_branches.append(branch_name.replace('origin/', ''))

    total_branches = len(local_branches) + len(remote_branches)

    if total_branches == 0:
        print_success("No Claude branches to cleanup")
    else:
        print_info(f"Found {len(local_branches)} local and {len(remote_branches)} remote branch(es)")

        # Delete local branches
        if local_branches:
            print_info("Deleting local branches...")
            for branch_name in local_branches:
                returncode, _, _ = run_command(f"git branch -D {branch_name}")
                if returncode == 0:
                    print_success(f"  [OK] Deleted local: {branch_name}")
                else:
                    print_warning(f"  [FAIL] Failed: {branch_name}")

        # Delete remote branches
        if remote_branches:
            print_info("Deleting remote branches...")
            branches_str = ' '.join(remote_branches)
            returncode, _, _ = run_command(f"git push origin --delete {branches_str}")

            if returncode == 0:
                print_success(f"  [OK] Deleted {len(remote_branches)} remote branch(es)")
            else:
                print_warning("  [FAIL] Some remote branches failed to delete")

        # Prune remote references
        print_info("Pruning remote references...")
        run_command("git fetch --prune")

        print_success("Step 3/3: Cleanup completed!")

    print()
    print_header("Automatic Workflow Completed Successfully!")
    print()
    print_success("[OK] Claude branches merged")
    print_success("[OK] Repository synced")
    print_success("[OK] Cleanup completed")
    print()

    return True

# ========== INTERACTIVE MENU ==========

def interactive_menu():
    """Show interactive menu with loop"""
    # Perform initial health check (only once)
    is_healthy, issues = check_git_repository_health()
    if not is_healthy and issues:
        print_warning("Repository health check found some issues:")
        for issue in issues[:3]:  # Show first 3 issues
            print(f"  • {issue}")
        if len(issues) > 3:
            print(f"  • ... and {len(issues) - 3} more")
        print()
        proceed = input("Continue anyway? (y/n): ").strip().lower()
        if proceed not in ['y', 'yes']:
            print_info("Exiting due to health check issues")
            return 1

    # Check for script updates (only once)
    has_updates, update_msg = check_script_updates()
    if has_updates:
        print_warning(update_msg)
        print_info("Consider pulling latest changes to get the newest version")
        print()

    while True:
        clear_screen()
        print_header("Safe Git Sync - Main Menu v4.4")

        # Get current state
        branch = get_current_branch()
        if not branch:
            print_error("Could not determine current branch!")
            return 1

        print(f"{Colors.CYAN}Current Branch:{Colors.END} {Colors.BOLD}{branch}{Colors.END}")

        # Warn if working on a Claude branch (should work on main instead)
        if branch.startswith('claude/'):
            print_warning("[WARN] You are on a Claude branch!")
            print_info(f"Claude branches should be merged to {DEFAULT_BRANCH}, not worked on directly")
            print_info(f"Use option 4 or 10 to auto-switch to {DEFAULT_BRANCH} and merge changes")
            print()

        # Fetch first
        if not fetch_remote(branch):
            print_warning("Could not fetch from remote")

        # Check for Claude branches ONLY if we're on main
        if branch == DEFAULT_BRANCH:
            claude_branches = get_claude_branches()
            if claude_branches:
                print()
                print_warning(f"Found {len(claude_branches)} new Claude branch(es) with updates!")
                for branch_info in claude_branches:
                    print(f"  • {branch_info['name']}: {len(branch_info['commits'])} commit(s)")

        # Check state
        uncommitted = check_git_status()
        unpushed = check_unpushed_commits(branch)
        local_ahead, remote_ahead = check_diverged_branches(branch)
        new_commits = get_new_commits(branch)

        print()
        print("Status:")
        if uncommitted:
            print_warning(f"{len(uncommitted)} uncommitted change(s)")
        else:
            print_success("Working tree clean")

        if unpushed:
            print_warning(f"{len(unpushed)} unpushed commit(s)")
        else:
            print_success("All commits pushed")

        if new_commits:
            print_warning(f"{len(new_commits)} new commit(s) on remote")
        else:
            print_success("Up to date with remote")

        if local_ahead > 0 and remote_ahead > 0:
            print_warning(f"Branches diverged (local +{local_ahead}, remote +{remote_ahead})")

        print()
        print("Options:")
        print(f"  {Colors.BOLD}1.{Colors.END} Pull from remote (fetch + merge)")
        print(f"  {Colors.BOLD}2.{Colors.END} Push to remote")
        print(f"  {Colors.BOLD}3.{Colors.END} Sync (pull + push)")
        print(f"  {Colors.BOLD}4.{Colors.END} Merge Claude branches to {DEFAULT_BRANCH}")
        print(f"  {Colors.BOLD}5.{Colors.END} Verify all Claude changes")
        print(f"  {Colors.BOLD}6.{Colors.END} Stash changes")
        print(f"  {Colors.BOLD}7.{Colors.END} View uncommitted changes")
        print(f"  {Colors.BOLD}8.{Colors.END} View unpushed commits")
        print(f"  {Colors.BOLD}9.{Colors.END} Cleanup merged Claude branches")
        print(f"  {Colors.BOLD}10.{Colors.END} Auto: Merge + Sync + Cleanup (no prompts)")
        print(f"  {Colors.BOLD}0.{Colors.END} Exit")

        choice = input(f"\n{Colors.BOLD}Your choice (0-10):{Colors.END} ").strip()

        if choice == "1":
            result = do_pull(branch, uncommitted, new_commits)
            input("\nPress Enter to continue...")
            if result != 0:
                continue
        elif choice == "2":
            result = do_push(branch, uncommitted, unpushed)
            input("\nPress Enter to continue...")
            if result != 0:
                continue
        elif choice == "3":
            result = do_sync(branch, uncommitted, unpushed, new_commits)
            input("\nPress Enter to continue...")
            if result != 0:
                continue
        elif choice == "4":
            # Auto-switch to main if needed
            success, original_branch = auto_switch_to_main_branch()
            if not success:
                input("\nPress Enter to continue...")
                continue

            # Merge Claude branches
            if check_and_merge_claude_branches():
                print_success("Claude branches merged! You can now push to GitHub.")
            input("\nPress Enter to continue...")
            continue
        elif choice == "5":
            verify_all_changes()
            input("\nPress Enter to continue...")
            continue
        elif choice == "6":
            result = do_stash()
            input("\nPress Enter to continue...")
            continue
        elif choice == "7":
            show_uncommitted_changes()
            input("\nPress Enter to continue...")
            continue
        elif choice == "8":
            show_unpushed_commits(branch)
            input("\nPress Enter to continue...")
            continue
        elif choice == "9":
            if cleanup_merged_claude_branches():
                print_success("All Claude branches cleaned up!")
            input("\nPress Enter to continue...")
            continue
        elif choice == "10":
            # Auto-switch to main if needed (no prompts — option 10 is fully automatic)
            success, original_branch = auto_switch_to_main_branch()
            if not success:
                print_error("Could not switch to main branch. Aborting auto workflow.")
                continue

            # Always use fast-forward/merge (strategy 1) — no user interaction
            if do_auto_workflow(DEFAULT_BRANCH, use_rebase=False):
                print_success("Automatic workflow completed successfully!")
            else:
                print_error("Automatic workflow failed. Check errors above.")
            continue
        elif choice == "0":
            print_info("Exiting...")
            return 0
        else:
            print_warning("Invalid choice! Please select 0-10.")
            input("\nPress Enter to continue...")
            continue

# ========== MAIN ENTRY POINT ==========

def main():
    """Main function"""
    global VERBOSE_MODE
    args = sys.argv[1:]

    # Check for verbose mode
    if "--verbose" in args or "-v" in args:
        VERBOSE_MODE = True
        args = [arg for arg in args if arg not in ["--verbose", "-v"]]
        print_info("Verbose mode enabled")

    # Handle CLI arguments
    if "--help" in args or "-h" in args:
        print(__doc__)
        return 0

    # Full Auto Mode - delegate to auto-git-sync.py
    if "--full-auto" in args or "--auto" in args:
        print_info("Running in FULL AUTO mode - delegating to auto-git-sync.py...")
        print_info("This will handle ALL synchronization tasks automatically.")
        print()

        # Check if auto-git-sync.py exists
        auto_sync_path = Path(__file__).parent / "auto-git-sync.py"
        if not auto_sync_path.exists():
            print_error("auto-git-sync.py not found!")
            print_info(f"Expected location: {auto_sync_path}")
            print_info("Please ensure auto-git-sync.py is in the same directory.")
            return 1

        # Prepare arguments for auto-git-sync.py
        auto_sync_args = []
        if VERBOSE_MODE:
            auto_sync_args.append("--verbose")
        if "--dry-run" in args:
            auto_sync_args.append("--dry-run")
        if "--force" in args:
            auto_sync_args.append("--force")

        # Run auto-git-sync.py
        import subprocess
        cmd = [sys.executable, str(auto_sync_path)] + auto_sync_args
        print_info(f"Executing: {' '.join(cmd)}")
        print()

        result = subprocess.run(cmd)
        return result.returncode

    if "--pull" in args:
        branch = get_current_branch()
        fetch_remote(branch)
        uncommitted = check_git_status()
        new_commits = get_new_commits(branch)
        return do_pull(branch, uncommitted, new_commits)

    elif "--push" in args:
        branch = get_current_branch()
        fetch_remote(branch)
        uncommitted = check_git_status()
        unpushed = check_unpushed_commits(branch)
        return do_push(branch, uncommitted, unpushed)

    elif "--sync" in args:
        branch = get_current_branch()
        fetch_remote(branch)
        uncommitted = check_git_status()
        unpushed = check_unpushed_commits(branch)
        new_commits = get_new_commits(branch)
        return do_sync(branch, uncommitted, unpushed, new_commits)

    elif "--merge-claude" in args:
        branch = get_current_branch()
        if branch != DEFAULT_BRANCH:
            print_error(f"Please switch to {DEFAULT_BRANCH} branch first!")
            print_info(f"Run: git checkout {DEFAULT_BRANCH}")
            return 1

        clear_screen()
        print_header("Merge Claude Branches to Main")
        if check_and_merge_claude_branches():
            print_success("All Claude branches merged successfully!")
            print_info(f"You can now push to GitHub: git push origin {DEFAULT_BRANCH}")
            return 0
        else:
            print_warning("No Claude branches to merge, or merge was cancelled.")
            return 0

    elif "--verify" in args:
        return 0 if verify_all_changes() else 1

    elif "--cleanup" in args:
        clear_screen()
        print_header("Cleanup Merged Claude Branches")
        if cleanup_merged_claude_branches():
            print_success("All Claude branches cleaned up successfully!")
            return 0
        else:
            print_warning("Cleanup was cancelled or no branches to clean.")
            return 0

    else:
        # Interactive menu
        return interactive_menu()

if __name__ == "__main__":
    sys.exit(main())
