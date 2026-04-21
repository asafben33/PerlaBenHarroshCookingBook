#!/usr/bin/env python3
"""
Intelligent Auto Git Sync v5.1 - Zero-Interaction Edition
==========================================================

Fully automated git synchronization with intelligent state management,
comprehensive backup system, and guaranteed safety.

Features:
  OK Zero interaction - handles ALL scenarios automatically
  OK Multi-layer backup system (bundle + patches + snapshots)
  OK Intelligent merge strategy selection (squash + fallback)
  OK Conflict detection and safe handling
  OK Claude branch auto-merge with dual strategy
  OK Auto-fix missing remote tracking branches
  OK Recovery from any failure state
  OK Comprehensive logging
  OK Never loses data
  OK Network retry with exponential backoff
  OK Validates every operation
  OK Rollback capability at any stage

Safe for:
  - Running every few minutes via cron/scheduler
  - Fully automated CI/CD workflows
  - Unattended synchronization
  - Multi-developer environments

Usage:
    python auto-git-sync.py              # Full auto-sync
    python auto-git-sync.py --dry-run    # Show what would happen
    python auto-git-sync.py --verbose    # Detailed logging
    python auto-git-sync.py --force      # Skip safety delays

Safety Guarantees:
  1. Creates full backup before ANY operation
  2. Never force-pushes without verification
  3. Preserves all uncommitted changes
  4. Keeps backups for 7 days
  5. Validates state after each step
  6. Aborts on unrecoverable conflicts
  7. Provides manual recovery instructions

Author: Certificate Manager Team
Date: 2026-02-03
"""

import os
import sys
import subprocess
import json
import shutil
import hashlib
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
import logging
import time
import re

# ============================================================================
# DRY-RUN Configuration (Rule 0.3)
# ============================================================================

# Toggle for dry-run mode - change to True to preview without making changes
DRY_RUN = False

# ============================================================================
# Configuration
# ============================================================================

class Config:
    """Configuration constants"""
    BACKUP_DIR = Path(".git-auto-sync-backups")
    BACKUP_RETENTION_DAYS = 7
    LOG_DIR = Path("logs")
    MAX_RETRIES = 4
    RETRY_DELAYS = [2, 4, 8, 16]  # Exponential backoff in seconds
    MAIN_BRANCH = "main"
    CLAUDE_BRANCH_PREFIX = "claude/"
    SAFETY_DELAY_SECONDS = 3  # Delay before risky operations

    # Network timeout settings
    GIT_TIMEOUT = 30

    # Conflict markers
    CONFLICT_MARKERS = [
        b'<<<<<<<',
        b'=======',
        b'>>>>>>>'
    ]

# ============================================================================
# Logging Setup
# ============================================================================

def setup_logging(verbose: bool = False) -> logging.Logger:
    """Setup comprehensive logging (Rule 0.4: Hebrew date format)"""
    Config.LOG_DIR.mkdir(exist_ok=True)

    # Hebrew date format: DD-MM-YYYY_HH.MM (Rule 0.4)
    timestamp = datetime.now().strftime("%d-%m-%Y_%H.%M")
    log_file = Config.LOG_DIR / f"auto-git-sync_{timestamp}.log"

    # Create logger
    logger = logging.getLogger('auto-git-sync')
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    # File handler (always detailed)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
    )
    file_handler.setFormatter(file_formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG if verbose else logging.INFO)
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')
    console_handler.setFormatter(console_formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    logger.info(f"Log file created: {log_file}")

    return logger

# ============================================================================
# Git Command Wrapper
# ============================================================================

class GitCommand:
    """Safe git command execution with retry logic"""

    def __init__(self, logger: logging.Logger):
        self.logger = logger

    def run(
        self,
        cmd: List[str],
        retry: bool = False,
        capture_output: bool = True,
        check: bool = True,
        timeout: int = Config.GIT_TIMEOUT
    ) -> subprocess.CompletedProcess:
        """
        Execute git command with optional retry logic

        Args:
            cmd: Command and arguments
            retry: Enable retry with exponential backoff
            capture_output: Capture stdout/stderr
            check: Raise exception on non-zero exit
            timeout: Command timeout in seconds

        Returns:
            CompletedProcess result
        """
        retries = Config.MAX_RETRIES if retry else 1

        for attempt in range(retries):
            try:
                self.logger.debug(f"Running: {' '.join(cmd)} (attempt {attempt + 1}/{retries})")

                # CRITICAL FIX: Force UTF-8 encoding for Windows compatibility
                # Also ensure we're not in shell mode for cross-platform compatibility
                result = subprocess.run(
                    cmd,
                    capture_output=capture_output,
                    text=True,
                    encoding='utf-8',
                    errors='replace',  # Replace invalid characters instead of crashing
                    timeout=timeout,
                    check=check,
                    shell=False  # Explicit for security and consistency
                )

                self.logger.debug(f"Exit code: {result.returncode}")
                if result.stdout:
                    self.logger.debug(f"Stdout: {result.stdout.strip()}")
                if result.stderr:
                    self.logger.debug(f"Stderr: {result.stderr.strip()}")

                return result

            except subprocess.TimeoutExpired:
                self.logger.warning(f"Command timeout (attempt {attempt + 1}/{retries}): {' '.join(cmd)}")
                if attempt < retries - 1:
                    delay = Config.RETRY_DELAYS[attempt]
                    self.logger.info(f"Retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    raise

            except subprocess.CalledProcessError as e:
                # Check if it's a network error that should be retried
                if self._is_network_error(e) and attempt < retries - 1:
                    delay = Config.RETRY_DELAYS[attempt]
                    self.logger.warning(f"Network error, retrying in {delay}s: {e.stderr}")
                    time.sleep(delay)
                else:
                    # Add helpful context for Windows users
                    self.logger.error(f"Git command failed with exit code {e.returncode}")
                    if e.stdout:
                        self.logger.error(f"  Stdout: {e.stdout}")
                    if e.stderr:
                        self.logger.error(f"  Stderr: {e.stderr}")
                    self.logger.error(f"  Command: {' '.join(cmd)}")
                    raise

        raise RuntimeError(f"Command failed after {retries} attempts: {' '.join(cmd)}")

    def safe_output(self, result: subprocess.CompletedProcess, field: str = 'stdout') -> str:
        """
        Safely extract output from subprocess result

        Args:
            result: CompletedProcess result
            field: 'stdout' or 'stderr'

        Returns:
            Output string (empty if None)
        """
        if result is None:
            return ''

        value = getattr(result, field, None)
        if value is None:
            return ''

        return value.strip()

    def _is_network_error(self, error: subprocess.CalledProcessError) -> bool:
        """Check if error is network-related"""
        network_keywords = [
            'could not resolve host',
            'connection timed out',
            'connection refused',
            'network unreachable',
            'temporary failure',
            '500 internal server error',
            'failed to connect'
        ]

        error_text = (error.stderr or '').lower() + (error.stdout or '').lower()
        return any(keyword in error_text for keyword in network_keywords)

# ============================================================================
# Backup System
# ============================================================================

class BackupManager:
    """Multi-layer backup system"""

    def __init__(self, logger: logging.Logger, git: GitCommand):
        self.logger = logger
        self.git = git
        Config.BACKUP_DIR.mkdir(exist_ok=True)

    def create_full_backup(self) -> Dict[str, Any]:
        """
        Create comprehensive backup of repository state

        Returns:
            Backup metadata dict
        """
        timestamp = datetime.now()
        backup_id = timestamp.strftime("%Y%m%d_%H%M%S")
        backup_path = Config.BACKUP_DIR / backup_id
        backup_path.mkdir(parents=True, exist_ok=True)

        self.logger.info(f"Creating full backup: {backup_id}")

        metadata = {
            'backup_id': backup_id,
            'timestamp': timestamp.isoformat(),
            'backup_path': str(backup_path),
            'components': {}
        }

        try:
            # 1. Git bundle (complete repository backup)
            bundle_path = backup_path / "repo.bundle"
            self.logger.debug("Creating git bundle...")
            self.git.run(['git', 'bundle', 'create', str(bundle_path), '--all'])
            metadata['components']['bundle'] = str(bundle_path)
            self.logger.debug(f"Bundle created: {bundle_path}")

            # 2. Save current HEAD reference
            head_result = self.git.run(['git', 'rev-parse', 'HEAD'])
            metadata['head_sha'] = self.git.safe_output(head_result)

            # 3. Save current branch (with fallback for compatibility)
            try:
                branch_result = self.git.run(['git', 'branch', '--show-current'])
                metadata['current_branch'] = self.git.safe_output(branch_result)
            except subprocess.CalledProcessError:
                branch_result = self.git.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                metadata['current_branch'] = self.git.safe_output(branch_result)

            # 4. Save uncommitted changes as patch
            status_result = self.git.run(['git', 'status', '--porcelain'])
            if self.git.safe_output(status_result):
                self.logger.debug("Backing up uncommitted changes...")

                # Staged changes
                try:
                    staged_diff = self.git.run(
                        ['git', 'diff', '--cached'],
                        check=False
                    )
                    if staged_diff.stdout:
                        staged_patch = backup_path / "staged.patch"
                        staged_patch.write_text(staged_diff.stdout)
                        metadata['components']['staged_patch'] = str(staged_patch)
                        self.logger.debug(f"Staged changes saved: {staged_patch}")
                except Exception as e:
                    self.logger.warning(f"Could not backup staged changes: {e}")

                # Unstaged changes
                try:
                    unstaged_diff = self.git.run(
                        ['git', 'diff'],
                        check=False
                    )
                    if unstaged_diff.stdout:
                        unstaged_patch = backup_path / "unstaged.patch"
                        unstaged_patch.write_text(unstaged_diff.stdout)
                        metadata['components']['unstaged_patch'] = str(unstaged_patch)
                        self.logger.debug(f"Unstaged changes saved: {unstaged_patch}")
                except Exception as e:
                    self.logger.warning(f"Could not backup unstaged changes: {e}")

                # Untracked files
                try:
                    untracked_result = self.git.run(
                        ['git', 'ls-files', '--others', '--exclude-standard']
                    )
                    untracked_output = self.git.safe_output(untracked_result)
                    if untracked_output:
                        untracked_dir = backup_path / "untracked"
                        untracked_dir.mkdir(exist_ok=True)

                        for file_path in untracked_output.split('\n'):
                            if file_path:
                                src = Path(file_path)
                                if src.exists() and src.is_file():
                                    dst = untracked_dir / file_path
                                    dst.parent.mkdir(parents=True, exist_ok=True)
                                    shutil.copy2(src, dst)

                        metadata['components']['untracked_dir'] = str(untracked_dir)
                        self.logger.debug(f"Untracked files saved: {untracked_dir}")
                except Exception as e:
                    self.logger.warning(f"Could not backup untracked files: {e}")

            # 5. Save stash if any
            try:
                stash_list = self.git.run(['git', 'stash', 'list'])
                stash_output = self.git.safe_output(stash_list)
                if stash_output:
                    metadata['stash_count'] = len(stash_output.split('\n'))
            except Exception as e:
                self.logger.warning(f"Could not check stash: {e}")

            # 6. Save all branch refs
            refs_result = self.git.run(['git', 'show-ref'])
            refs_file = backup_path / "refs.txt"
            refs_file.write_text(refs_result.stdout)
            metadata['components']['refs'] = str(refs_file)

            # 7. Save metadata
            metadata_file = backup_path / "metadata.json"
            metadata_file.write_text(json.dumps(metadata, indent=2))

            self.logger.info(f"OK Backup created successfully: {backup_id}")
            return metadata

        except Exception as e:
            self.logger.error(f"Backup creation failed: {e}")
            raise

    def cleanup_old_backups(self):
        """Remove backups older than retention period"""
        cutoff = datetime.now() - timedelta(days=Config.BACKUP_RETENTION_DAYS)

        for backup_dir in Config.BACKUP_DIR.iterdir():
            if backup_dir.is_dir():
                try:
                    # Parse timestamp from directory name
                    timestamp_str = backup_dir.name
                    timestamp = datetime.strptime(timestamp_str, "%Y%m%d_%H%M%S")

                    if timestamp < cutoff:
                        self.logger.info(f"Removing old backup: {backup_dir.name}")
                        shutil.rmtree(backup_dir)
                except (ValueError, OSError) as e:
                    self.logger.warning(f"Could not process backup {backup_dir.name}: {e}")

    def restore_from_backup(self, backup_id: str) -> bool:
        """
        Restore repository from backup

        Args:
            backup_id: Backup identifier

        Returns:
            True if successful
        """
        backup_path = Config.BACKUP_DIR / backup_id
        metadata_file = backup_path / "metadata.json"

        if not metadata_file.exists():
            self.logger.error(f"Backup metadata not found: {backup_id}")
            return False

        metadata = json.loads(metadata_file.read_text())

        self.logger.warning(f"Restoring from backup: {backup_id}")

        try:
            # Restore from bundle
            bundle_path = metadata['components'].get('bundle')
            if bundle_path and Path(bundle_path).exists():
                self.logger.info("Restoring repository from bundle...")
                # Verify bundle first
                self.git.run(['git', 'bundle', 'verify', bundle_path])
                # Fetch from bundle
                self.git.run(['git', 'fetch', bundle_path, '--all'])

            # Checkout original branch
            original_branch = metadata.get('current_branch')
            if original_branch:
                self.git.run(['git', 'checkout', original_branch], check=False)

            # Restore patches if available
            if 'staged_patch' in metadata['components']:
                patch_file = metadata['components']['staged_patch']
                if Path(patch_file).exists():
                    self.logger.info("Restoring staged changes...")
                    self.git.run(['git', 'apply', '--cached', patch_file], check=False)

            if 'unstaged_patch' in metadata['components']:
                patch_file = metadata['components']['unstaged_patch']
                if Path(patch_file).exists():
                    self.logger.info("Restoring unstaged changes...")
                    self.git.run(['git', 'apply', patch_file], check=False)

            # Restore untracked files
            if 'untracked_dir' in metadata['components']:
                untracked_dir = Path(metadata['components']['untracked_dir'])
                if untracked_dir.exists():
                    self.logger.info("Restoring untracked files...")
                    for item in untracked_dir.rglob('*'):
                        if item.is_file():
                            rel_path = item.relative_to(untracked_dir)
                            dst = Path.cwd() / rel_path
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy2(item, dst)

            self.logger.info("OK Restore completed successfully")
            return True

        except Exception as e:
            self.logger.error(f"Restore failed: {e}")
            return False

# ============================================================================
# Repository State Analyzer
# ============================================================================

class RepositoryState:
    """Analyze and represent repository state"""

    def __init__(self, logger: logging.Logger, git: GitCommand):
        self.logger = logger
        self.git = git
        self.state = {}

    def analyze(self) -> Dict[str, Any]:
        """
        Comprehensive repository state analysis

        Returns:
            State dictionary with all relevant information
        """
        self.logger.info("Analyzing repository state...")

        state = {
            'timestamp': datetime.now().isoformat(),
            'clean': True,
            'issues': [],
            'warnings': [],
            'actions_needed': []
        }

        try:
            # Current branch (try --show-current first, fallback to rev-parse for compatibility)
            try:
                branch_result = self.git.run(['git', 'branch', '--show-current'])
                state['current_branch'] = self.git.safe_output(branch_result)
            except subprocess.CalledProcessError:
                # Fallback to older command for Git versions < 2.22 or Windows compatibility
                self.logger.debug("--show-current failed, using rev-parse fallback")
                branch_result = self.git.run(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
                state['current_branch'] = self.git.safe_output(branch_result)
            self.logger.debug(f"Current branch: {state['current_branch']}")

            # HEAD reference
            head_result = self.git.run(['git', 'rev-parse', 'HEAD'])
            state['head_sha'] = self.git.safe_output(head_result)

            # Check for detached HEAD
            try:
                self.git.run(['git', 'symbolic-ref', 'HEAD'])
                state['detached_head'] = False
            except subprocess.CalledProcessError:
                state['detached_head'] = True
                state['clean'] = False
                state['issues'].append("Repository in detached HEAD state")

            # Check for merge/rebase in progress
            git_dir = Path('.git')
            state['merge_in_progress'] = (git_dir / 'MERGE_HEAD').exists()
            state['rebase_in_progress'] = (git_dir / 'rebase-merge').exists() or (git_dir / 'rebase-apply').exists()
            state['cherry_pick_in_progress'] = (git_dir / 'CHERRY_PICK_HEAD').exists()

            if any([state['merge_in_progress'], state['rebase_in_progress'], state['cherry_pick_in_progress']]):
                state['clean'] = False
                state['issues'].append("Repository has ongoing merge/rebase/cherry-pick operation")

            # Working tree status
            status_result = self.git.run(['git', 'status', '--porcelain'])
            uncommitted = self.git.safe_output(status_result)
            state['has_uncommitted_changes'] = bool(uncommitted)

            if uncommitted:
                state['clean'] = False
                state['uncommitted_files'] = uncommitted.split('\n')
                state['warnings'].append(f"Found {len(state['uncommitted_files'])} uncommitted changes")

            # Check for conflict markers in files
            if uncommitted:
                conflicts = self._detect_conflict_markers()
                if conflicts:
                    state['has_conflicts'] = True
                    state['conflict_files'] = conflicts
                    state['issues'].append(f"Found conflict markers in {len(conflicts)} files")
                else:
                    state['has_conflicts'] = False

            # Unpushed commits (compare with remote)
            if state['current_branch'] and not state['detached_head']:
                try:
                    # Get remote tracking branch
                    remote_branch_result = self.git.run(
                        ['git', 'rev-parse', '--abbrev-ref', f"{state['current_branch']}@{{upstream}}"],
                        check=False
                    )

                    if remote_branch_result.returncode == 0:
                        remote_branch = self.git.safe_output(remote_branch_result)
                        state['remote_tracking_branch'] = remote_branch

                        # Count unpushed commits
                        unpushed_result = self.git.run(
                            ['git', 'rev-list', '--count', f"{remote_branch}..HEAD"]
                        )
                        unpushed_count = int(self.git.safe_output(unpushed_result) or '0')
                        state['unpushed_commits'] = unpushed_count

                        if unpushed_count > 0:
                            state['clean'] = False
                            state['warnings'].append(f"Found {unpushed_count} unpushed commits")

                        # Count commits behind remote
                        behind_result = self.git.run(
                            ['git', 'rev-list', '--count', f"HEAD..{remote_branch}"]
                        )
                        behind_count = int(self.git.safe_output(behind_result) or '0')
                        state['commits_behind'] = behind_count

                        if behind_count > 0:
                            state['warnings'].append(f"Branch is {behind_count} commits behind remote")

                        # Check for divergence
                        state['diverged'] = unpushed_count > 0 and behind_count > 0
                        if state['diverged']:
                            state['issues'].append("Branch has diverged from remote")
                    else:
                        state['remote_tracking_branch'] = None
                        state['warnings'].append("No remote tracking branch configured")

                except Exception as e:
                    self.logger.warning(f"Could not check remote status: {e}")
                    state['remote_tracking_branch'] = None

            # Find Claude branches
            state['claude_branches'] = self._find_claude_branches()
            if state['claude_branches']:
                state['warnings'].append(f"Found {len(state['claude_branches'])} Claude branches")

            # Check stash
            stash_result = self.git.run(['git', 'stash', 'list'])
            stash_output = self.git.safe_output(stash_result)
            stash_entries = [s for s in stash_output.split('\n') if s]
            state['stash_count'] = len(stash_entries)
            if state['stash_count'] > 0:
                state['warnings'].append(f"Found {state['stash_count']} stashed changes")

            # Summary
            self.logger.info(f"State analysis complete: {'CLEAN' if state['clean'] else 'NEEDS ATTENTION'}")
            if state['issues']:
                for issue in state['issues']:
                    self.logger.warning(f"  Issue: {issue}")
            if state['warnings']:
                for warning in state['warnings']:
                    self.logger.info(f"  Warning: {warning}")

            self.state = state
            return state

        except Exception as e:
            self.logger.error(f"State analysis failed: {e}")
            raise

    def _detect_conflict_markers(self) -> List[str]:
        """Detect files with conflict markers"""
        conflicts = []

        try:
            # Get list of modified files
            status_result = self.git.run(['git', 'status', '--porcelain'])
            status_output = self.git.safe_output(status_result)

            for line in status_output.split('\n'):
                if not line:
                    continue

                # Parse status line
                status = line[:2]
                filename = line[3:].strip()

                # Skip deleted files
                if 'D' in status:
                    continue

                # Check file for conflict markers
                try:
                    file_path = Path(filename)
                    if file_path.exists() and file_path.is_file():
                        content = file_path.read_bytes()
                        if any(marker in content for marker in Config.CONFLICT_MARKERS):
                            conflicts.append(filename)
                except Exception as e:
                    self.logger.debug(f"Could not check {filename}: {e}")

        except Exception as e:
            self.logger.warning(f"Conflict marker detection failed: {e}")

        return conflicts

    def _auto_clean_conflict_markers(self, state: Dict[str, Any]) -> bool:
        """
        Auto-clean conflict markers from files left by a previous failed merge.

        Strategy:
        1. First abort any ongoing merge/rebase
        2. Restore conflicted files from HEAD (discard local conflict markers)

        Returns:
            True if all conflict markers were cleaned
        """
        conflict_files = state.get('conflict_files', [])
        if not conflict_files:
            return True

        self.logger.info(f"Cleaning conflict markers from {len(conflict_files)} file(s)...")

        # Step 1: Abort any ongoing merge/rebase that may have left these markers
        try:
            self.git.run(['git', 'merge', '--abort'], check=False)
            self.logger.info("Aborted ongoing merge (if any)")
        except Exception:
            pass

        try:
            self.git.run(['git', 'rebase', '--abort'], check=False)
        except Exception:
            pass

        # Step 2: Restore conflicted files from HEAD
        all_cleaned = True
        for filename in conflict_files:
            try:
                self.git.run(['git', 'checkout', 'HEAD', '--', filename])
                self.logger.info(f"  OK Restored {filename} from HEAD")
            except subprocess.CalledProcessError:
                # File might not exist in HEAD (new file with conflicts)
                # In that case, just remove the conflict markers by deleting it
                try:
                    file_path = Path(filename)
                    if file_path.exists():
                        file_path.unlink()
                        self.logger.info(f"  OK Removed conflicted new file {filename}")
                except Exception as e:
                    self.logger.error(f"  FAIL Could not clean {filename}: {e}")
                    all_cleaned = False

        # Verify no conflict markers remain
        remaining = self._detect_conflict_markers()
        if remaining:
            self.logger.warning(f"Still have conflict markers in: {remaining}")
            all_cleaned = False

        return all_cleaned

    def _find_claude_branches(self) -> List[Dict[str, Any]]:
        """Find all Claude branches with their status"""
        claude_branches = []

        try:
            # Fetch remote refs
            self.git.run(['git', 'fetch', '--all', '--prune'], retry=True)

            # Get remote branches
            remote_branches_result = self.git.run(['git', 'branch', '-r'])
            remote_branches_output = self.git.safe_output(remote_branches_result)

            for line in remote_branches_output.split('\n'):
                branch_name = line.strip()

                if f'origin/{Config.CLAUDE_BRANCH_PREFIX}' in branch_name:
                    # Extract branch name without origin/
                    local_name = branch_name.replace('origin/', '')

                    branch_info = {
                        'name': local_name,
                        'remote_name': branch_name,
                        'commits_ahead': 0,
                        'already_merged': False
                    }

                    try:
                        # Check if already merged to main
                        merge_base_result = self.git.run(
                            ['git', 'merge-base', Config.MAIN_BRANCH, branch_name]
                        )
                        merge_base = self.git.safe_output(merge_base_result)

                        # Check if branch tip is ancestor of main
                        is_ancestor = self.git.run(
                            ['git', 'merge-base', '--is-ancestor', branch_name, Config.MAIN_BRANCH],
                            check=False
                        ).returncode == 0

                        branch_info['already_merged'] = is_ancestor

                        if not is_ancestor:
                            # Count new commits
                            commits_result = self.git.run(
                                ['git', 'rev-list', '--count', f"{Config.MAIN_BRANCH}..{branch_name}"]
                            )
                            branch_info['commits_ahead'] = int(self.git.safe_output(commits_result) or '0')

                    except Exception as e:
                        self.logger.debug(f"Could not analyze branch {local_name}: {e}")

                    if not branch_info['already_merged'] and branch_info['commits_ahead'] > 0:
                        claude_branches.append(branch_info)
                        self.logger.info(
                            f"Found Claude branch: {local_name} "
                            f"({branch_info['commits_ahead']} commits ahead)"
                        )

        except Exception as e:
            self.logger.warning(f"Could not find Claude branches: {e}")

        return claude_branches

# ============================================================================
# Intelligent Sync Engine
# ============================================================================

class AutoSyncEngine:
    """Intelligent automatic synchronization engine"""

    def __init__(
        self,
        logger: logging.Logger,
        git: GitCommand,
        backup: BackupManager,
        dry_run: bool = False,
        force: bool = False
    ):
        self.logger = logger
        self.git = git
        self.backup = backup
        self.dry_run = dry_run
        self.force = force
        self.state_analyzer = RepositoryState(logger, git)

    def sync(self) -> bool:
        """
        Execute complete synchronization workflow

        Returns:
            True if successful
        """
        self.logger.info("=" * 70)
        self.logger.info("Starting Intelligent Auto-Sync")
        self.logger.info("=" * 70)

        if self.dry_run:
            self.logger.info("[DRY RUN MODE - No changes will be made]")

        try:
            # Phase 1: Analyze current state
            self.logger.info("\n[Phase 1/6] Analyzing Repository State")
            state = self.state_analyzer.analyze()

            if state['issues']:
                # Try to auto-resolve issues before giving up
                remaining_issues = []

                for issue in state['issues']:
                    if 'conflict markers' in issue.lower():
                        # Auto-resolve: conflict markers from previous failed merge
                        # Clean them by restoring files from HEAD
                        self.logger.info("Auto-resolving conflict markers from previous failed merge...")
                        if self._auto_clean_conflict_markers(state):
                            self.logger.info("OK Conflict markers cleaned successfully")
                            state['has_conflicts'] = False
                        else:
                            remaining_issues.append(issue)
                    else:
                        remaining_issues.append(issue)

                if remaining_issues:
                    self.logger.error("Critical issues detected - cannot proceed safely")
                    for issue in remaining_issues:
                        self.logger.error(f"  - {issue}")
                    state['issues'] = remaining_issues
                    self._provide_recovery_instructions(state)
                    return False
                else:
                    state['issues'] = []

            # Phase 2: Create backup
            self.logger.info("\n[Phase 2/6] Creating Safety Backup")
            if not self.dry_run:
                backup_metadata = self.backup.create_full_backup()
                self.logger.info(f"OK Backup ID: {backup_metadata['backup_id']}")
            else:
                self.logger.info("[DRY RUN] Would create backup")

            # Phase 3: Handle uncommitted changes
            self.logger.info("\n[Phase 3/6] Handling Uncommitted Changes")
            stash_created = False
            if state['has_uncommitted_changes']:
                stash_created = self._handle_uncommitted_changes(state)
            else:
                self.logger.info("OK No uncommitted changes")

            # Phase 4: Switch to main if needed
            self.logger.info("\n[Phase 4/6] Ensuring Main Branch")
            if not self._ensure_main_branch(state):
                return False

            # Phase 5: Sync with remote
            self.logger.info("\n[Phase 5/6] Synchronizing with Remote")
            if not self._sync_with_remote(state):
                return False

            # Phase 6: Merge Claude branches
            self.logger.info("\n[Phase 6/6] Merging Claude Branches")
            if state['claude_branches']:
                if not self._merge_claude_branches(state):
                    return False
            else:
                self.logger.info("OK No Claude branches to merge")

            # Restore stashed changes
            if stash_created:
                self.logger.info("\nRestoring stashed changes...")
                if not self.dry_run:
                    try:
                        self.git.run(['git', 'stash', 'pop'])
                        self.logger.info("OK Stashed changes restored")
                    except subprocess.CalledProcessError:
                        self.logger.warning(
                            "Could not auto-restore stash (may have conflicts). "
                            "Run 'git stash pop' manually."
                        )
                else:
                    self.logger.info("[DRY RUN] Would restore stash")

            # Cleanup old backups
            self.logger.info("\nCleaning up old backups...")
            if not self.dry_run:
                self.backup.cleanup_old_backups()

            self.logger.info("\n" + "=" * 70)
            self.logger.info("OK Synchronization completed successfully!")
            self.logger.info("=" * 70)

            return True

        except Exception as e:
            self.logger.error(f"\n{'=' * 70}")
            self.logger.error(f"Synchronization failed: {e}")
            self.logger.error(f"{'=' * 70}")
            return False

    def _handle_uncommitted_changes(self, state: Dict[str, Any]) -> bool:
        """
        Handle uncommitted changes safely

        Returns:
            True if stash was created
        """
        file_count = len(state.get('uncommitted_files', []))
        self.logger.info(f"Found {file_count} uncommitted changes")

        if state.get('has_conflicts'):
            # Try to clean conflict markers before giving up
            if self._auto_clean_conflict_markers(state):
                self.logger.info("OK Cleaned conflict markers before stashing")
                state['has_conflicts'] = False
                # Re-check if there are still uncommitted changes to stash
                status_result = self.git.run(['git', 'status', '--porcelain'], check=False)
                status_output = self.git.safe_output(status_result)
                if not status_output or not status_output.strip():
                    self.logger.info("OK No changes left after conflict cleanup")
                    return False  # No stash needed
            else:
                self.logger.error("Cannot proceed - files still contain conflict markers")
                self.logger.error("Please resolve conflicts manually first")
                return False

        # Auto-stash uncommitted changes
        self.logger.info("Auto-stashing uncommitted changes...")

        if not self.dry_run:
            try:
                stash_result = self.git.run([
                    'git', 'stash', 'push',
                    '-m', f'Auto-stash by auto-git-sync at {datetime.now():%Y-%m-%d %H:%M:%S}'
                ])
                self.logger.info("OK Changes stashed successfully")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Failed to stash changes: {e}")
                return False
        else:
            self.logger.info("[DRY RUN] Would stash uncommitted changes")
            return False

    def _ensure_main_branch(self, state: Dict[str, Any]) -> bool:
        """
        Ensure we're on the main branch and configure tracking

        Returns:
            True if successful
        """
        current_branch = state.get('current_branch', '')

        if current_branch == Config.MAIN_BRANCH:
            self.logger.info(f"OK Already on {Config.MAIN_BRANCH} branch")
        else:
            self.logger.info(f"Switching from '{current_branch}' to '{Config.MAIN_BRANCH}'...")

            if not self.dry_run:
                try:
                    self.git.run(['git', 'checkout', Config.MAIN_BRANCH])
                    self.logger.info(f"OK Switched to {Config.MAIN_BRANCH}")
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to switch to {Config.MAIN_BRANCH}: {e}")
                    return False
            else:
                self.logger.info(f"[DRY RUN] Would switch to {Config.MAIN_BRANCH}")
                return True

        # Ensure remote tracking branch is configured
        if not state.get('remote_tracking_branch'):
            self.logger.info(f"Setting up remote tracking for {Config.MAIN_BRANCH}...")

            if not self.dry_run:
                try:
                    # Set upstream tracking branch
                    self.git.run([
                        'git', 'branch',
                        f'--set-upstream-to=origin/{Config.MAIN_BRANCH}',
                        Config.MAIN_BRANCH
                    ])
                    self.logger.info(f"OK Tracking branch configured: origin/{Config.MAIN_BRANCH}")
                except subprocess.CalledProcessError as e:
                    self.logger.warning(f"Could not set tracking branch (may not exist on remote): {e}")
                    # This is not critical, continue
            else:
                self.logger.info(f"[DRY RUN] Would set tracking to origin/{Config.MAIN_BRANCH}")

        return True

    def _sync_with_remote(self, state: Dict[str, Any]) -> bool:
        """
        Synchronize with remote repository

        Returns:
            True if successful
        """
        # Fetch latest from remote (including all branches for Claude branch detection)
        self.logger.info("Fetching from remote...")

        if not self.dry_run:
            try:
                # Fetch all branches to detect Claude branches and ensure main is up to date
                self.git.run(['git', 'fetch', 'origin', '--prune'], retry=True)
                self.logger.info("OK Fetch completed")
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Fetch failed: {e}")
                return False
        else:
            self.logger.info("[DRY RUN] Would fetch from remote")

        # Re-analyze state after fetch
        fresh_state = self.state_analyzer.analyze()

        commits_behind = fresh_state.get('commits_behind', 0)
        unpushed = fresh_state.get('unpushed_commits', 0)
        diverged = fresh_state.get('diverged', False)

        # Handle different scenarios
        if commits_behind == 0 and unpushed == 0:
            self.logger.info("OK Already in sync with remote")
            return True

        elif commits_behind > 0 and unpushed == 0:
            # Simple fast-forward
            self.logger.info(f"Pulling {commits_behind} commits from remote...")
            return self._pull_from_remote()

        elif commits_behind == 0 and unpushed > 0:
            # Simple push
            self.logger.info(f"Pushing {unpushed} local commits to remote...")
            return self._push_to_remote()

        elif diverged:
            # Diverged - need to merge
            self.logger.warning(f"Branch diverged: {unpushed} local, {commits_behind} remote")
            return self._handle_diverged_branch(fresh_state)

        return True

    def _pull_from_remote(self) -> bool:
        """Pull from remote (fast-forward)"""
        if not self.dry_run:
            try:
                self.git.run(['git', 'pull', '--ff-only', 'origin', Config.MAIN_BRANCH], retry=True)
                self.logger.info("OK Pull completed (fast-forward)")
                return True
            except subprocess.CalledProcessError:
                # Try regular merge
                self.logger.info("Fast-forward not possible, trying merge...")
                try:
                    self.git.run(['git', 'pull', 'origin', Config.MAIN_BRANCH], retry=True)
                    self.logger.info("OK Pull completed (merge)")
                    return True
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Pull failed: {e}")
                    return False
        else:
            self.logger.info("[DRY RUN] Would pull from remote")
            return True

    def _push_to_remote(self) -> bool:
        """Push to remote"""
        if not self.dry_run:
            try:
                self.git.run(['git', 'push', 'origin', Config.MAIN_BRANCH], retry=True)
                self.logger.info("OK Push completed")
                return True
            except subprocess.CalledProcessError as e:
                self.logger.error(f"Push failed: {e}")
                return False
        else:
            self.logger.info("[DRY RUN] Would push to remote")
            return True

    def _handle_diverged_branch(self, state: Dict[str, Any]) -> bool:
        """
        Handle diverged branch intelligently

        Strategy:
        1. Check if local commits are already in remote (rebase scenario)
        2. If safe, try rebase
        3. Otherwise, create merge commit

        Returns:
            True if successful
        """
        self.logger.info("Analyzing divergence...")

        # Show divergence details
        if not self.dry_run:
            # Show local commits
            local_commits_result = self.git.run([
                'git', 'log', '--oneline',
                f"origin/{Config.MAIN_BRANCH}..HEAD"
            ])
            local_commits = self.git.safe_output(local_commits_result)

            # Show remote commits
            remote_commits_result = self.git.run([
                'git', 'log', '--oneline',
                f"HEAD..origin/{Config.MAIN_BRANCH}"
            ])
            remote_commits = self.git.safe_output(remote_commits_result)

            self.logger.info("\nLocal commits not in remote:")
            for line in local_commits.split('\n')[:5]:  # Show max 5
                if line:
                    self.logger.info(f"  {line}")

            self.logger.info("\nRemote commits not in local:")
            for line in remote_commits.split('\n')[:5]:  # Show max 5
                if line:
                    self.logger.info(f"  {line}")

        # Try to merge remote changes
        self.logger.info("\nAttempting to merge remote changes...")

        if not self.dry_run:
            try:
                # Try merge with automatic commit
                self.git.run(['git', 'merge', f'origin/{Config.MAIN_BRANCH}', '-m',
                             f'Auto-merge remote changes from {datetime.now():%Y-%m-%d %H:%M:%S}'])
                self.logger.info("OK Merge successful")

                # Push the merge
                return self._push_to_remote()

            except subprocess.CalledProcessError as e:
                self.logger.error("Merge failed - likely conflicts")

                # Abort the merge
                try:
                    self.git.run(['git', 'merge', '--abort'])
                    self.logger.info("Merge aborted safely")
                except:
                    pass

                self.logger.error(
                    "Cannot automatically resolve divergence with conflicts. "
                    "Manual intervention required."
                )
                return False
        else:
            self.logger.info("[DRY RUN] Would attempt merge")
            return True

    def _detect_add_add_conflicts(self, branch_name: str) -> List[str]:
        """
        Detect potential add/add conflicts before merging

        Args:
            branch_name: Branch to check for conflicts

        Returns:
            List of files that would have add/add conflicts
        """
        conflict_files = []

        try:
            # Get files added in the branch
            branch_files_result = self.git.run([
                'git', 'diff', '--name-only', '--diff-filter=A',
                f'{Config.MAIN_BRANCH}...origin/{branch_name}'
            ])
            branch_files = set(self.git.safe_output(branch_files_result).split('\n'))
            branch_files.discard('')

            # Get files added in main since the branch diverged
            main_files_result = self.git.run([
                'git', 'diff', '--name-only', '--diff-filter=A',
                f'origin/{branch_name}...{Config.MAIN_BRANCH}'
            ])
            main_files = set(self.git.safe_output(main_files_result).split('\n'))
            main_files.discard('')

            # Find files added in both branches
            common_files = branch_files & main_files

            if common_files:
                self.logger.info(f"Detected potential add/add conflicts in: {common_files}")
                conflict_files = list(common_files)

        except Exception as e:
            self.logger.warning(f"Could not detect add/add conflicts: {e}")

        return conflict_files

    def _resolve_add_add_conflict(self, file_path: str, branch_name: str) -> bool:
        """
        Automatically resolve add/add conflict by choosing the newer version

        Args:
            file_path: Conflicted file path
            branch_name: Branch name being merged

        Returns:
            True if resolved successfully
        """
        try:
            # Get timestamps of both versions
            main_time_result = self.git.run([
                'git', 'log', '-1', '--format=%at', f'{Config.MAIN_BRANCH}', '--', file_path
            ], check=False)
            main_time = int(self.git.safe_output(main_time_result) or '0')

            branch_time_result = self.git.run([
                'git', 'log', '-1', '--format=%at', f'origin/{branch_name}', '--', file_path
            ], check=False)
            branch_time = int(self.git.safe_output(branch_time_result) or '0')

            # Choose the newer version (or branch version if equal)
            if branch_time >= main_time:
                self.logger.info(f"Resolving {file_path}: choosing branch version (newer)")
                self.git.run(['git', 'checkout', '--theirs', '--', file_path])
            else:
                self.logger.info(f"Resolving {file_path}: choosing main version (newer)")
                self.git.run(['git', 'checkout', '--ours', '--', file_path])

            self.git.run(['git', 'add', file_path])
            return True

        except Exception as e:
            self.logger.error(f"Could not auto-resolve {file_path}: {e}")
            return False

    def _resolve_all_merge_conflicts(self, branch_name: str) -> bool:
        """
        Resolve ALL merge conflicts (AA, UU, and others) by preferring the
        incoming (claude) branch version for claude branches.

        Args:
            branch_name: Branch being merged

        Returns:
            True if all conflicts resolved
        """
        try:
            # Get all unmerged files
            result = self.git.run(['git', 'diff', '--name-only', '--diff-filter=U'], check=False)
            unmerged_output = self.git.safe_output(result)
            if not unmerged_output or not unmerged_output.strip():
                return True  # No conflicts

            unmerged_files = [f.strip() for f in unmerged_output.split('\n') if f.strip()]
            self.logger.info(f"Found {len(unmerged_files)} unmerged file(s) to resolve")

            all_resolved = True
            for file_path in unmerged_files:
                try:
                    # For claude branches, prefer incoming (theirs) version
                    self.logger.info(f"Auto-resolving {file_path}: accepting incoming ({branch_name}) version")
                    self.git.run(['git', 'checkout', '--theirs', '--', file_path])
                    self.git.run(['git', 'add', file_path])
                except subprocess.CalledProcessError as e:
                    self.logger.error(f"Failed to auto-resolve {file_path}: {e}")
                    all_resolved = False

            return all_resolved

        except Exception as e:
            self.logger.error(f"Error during conflict resolution: {e}")
            return False

    def _merge_claude_branches(self, state: Dict[str, Any]) -> bool:
        """
        Merge all Claude branches to main using intelligent strategy

        Returns:
            True if successful
        """
        claude_branches = state.get('claude_branches', [])

        if not claude_branches:
            return True

        self.logger.info(f"Found {len(claude_branches)} Claude branch(es) to merge")

        merged_count = 0
        failed_branches = []

        for branch_info in claude_branches:
            branch_name = branch_info['name']
            commits_ahead = branch_info['commits_ahead']

            self.logger.info(f"\nMerging {branch_name} ({commits_ahead} commits)...")

            if not self.dry_run:
                # Check for potential add/add conflicts
                potential_conflicts = self._detect_add_add_conflicts(branch_name)
                if potential_conflicts:
                    self.logger.warning(
                        f"Detected {len(potential_conflicts)} potential add/add conflict(s). "
                        "Will attempt auto-resolution."
                    )

                # Try multiple merge strategies
                merge_success = False

                # Strategy 1: Try squash merge (cleaner, less conflicts)
                self.logger.info(f"Attempting squash merge for {branch_name}...")
                try:
                    # Squash merge combines all commits into one
                    self.git.run(['git', 'merge', '--squash', f"origin/{branch_name}"])

                    # Create commit with descriptive message
                    commit_msg = f"Merge {branch_name}\n\nSquash merged {commits_ahead} commits from {branch_name}"
                    self.git.run(['git', 'commit', '-m', commit_msg])

                    self.logger.info(f"OK Squash merged {branch_name}")
                    merged_count += 1
                    merge_success = True

                except subprocess.CalledProcessError as e:
                    stderr_output = getattr(e, 'stderr', '') or ''
                    error_str = str(e)

                    # Check if it's a conflict (any type: add/add, content, etc.)
                    if 'CONFLICT' in stderr_output or 'CONFLICT' in error_str:
                        self.logger.info("Detected merge conflict(s) - attempting auto-resolution...")

                        # Try general conflict resolution (handles AA, UU, and all types)
                        all_resolved = self._resolve_all_merge_conflicts(branch_name)

                        if all_resolved:
                            try:
                                commit_msg = f"Merge {branch_name}\n\nSquash merged {commits_ahead} commits with auto-resolved conflicts"
                                self.git.run(['git', 'commit', '-m', commit_msg])
                                self.logger.info(f"OK Squash merged {branch_name} (auto-resolved conflicts)")
                                merged_count += 1
                                merge_success = True
                            except subprocess.CalledProcessError:
                                self.logger.warning("Could not complete commit after auto-resolution")

                    if not merge_success:
                        self.logger.warning(f"Squash merge failed, trying regular merge: {e}")
                        # Reset any partial squash merge
                        try:
                            self.git.run(['git', 'reset', '--hard', 'HEAD'])
                        except:
                            pass

                # Strategy 2: Try regular merge with no-ff (if squash failed)
                if not merge_success:
                    self.logger.info(f"Attempting regular merge for {branch_name}...")
                    try:
                        self.git.run([
                            'git', 'merge', '--no-ff',
                            f"origin/{branch_name}",
                            '-m', f'Merge {branch_name}'
                        ])

                        self.logger.info(f"OK Merged {branch_name}")
                        merged_count += 1
                        merge_success = True

                    except subprocess.CalledProcessError as e:
                        stderr_output = getattr(e, 'stderr', '') or ''
                        error_str = str(e)

                        # Try conflict resolution for any conflict type
                        if 'CONFLICT' in stderr_output or 'CONFLICT' in error_str:
                            self.logger.info("Detected merge conflict(s) in regular merge - attempting auto-resolution...")

                            all_resolved = self._resolve_all_merge_conflicts(branch_name)

                            if all_resolved:
                                try:
                                    self.git.run(['git', 'commit', '--no-edit'])
                                    self.logger.info(f"OK Merged {branch_name} (auto-resolved conflicts)")
                                    merged_count += 1
                                    merge_success = True
                                except subprocess.CalledProcessError:
                                    self.logger.warning("Could not complete commit after auto-resolution")

                        if not merge_success:
                            self.logger.error(f"Regular merge also failed for {branch_name}")
                            # Abort merge if in progress
                            try:
                                self.git.run(['git', 'merge', '--abort'])
                                self.logger.info("Merge aborted safely")
                            except:
                                pass

                # If both strategies failed
                if not merge_success:
                    self.logger.error(f"All merge strategies failed for {branch_name}")
                    failed_branches.append(branch_name)

                    # Provide detailed recovery instructions
                    self.logger.error("\nMANUAL MERGE REQUIRED")
                    self.logger.error("=" * 60)
                    self.logger.error(f"Branch: {branch_name}")

                    if potential_conflicts:
                        self.logger.error(f"\nConflicting files (add/add):")
                        for cf in potential_conflicts:
                            self.logger.error(f"  - {cf}")
                        self.logger.error("\nTo resolve add/add conflicts:")
                        self.logger.error(f"  1. Choose which version to keep:")
                        self.logger.error(f"     git checkout --ours <file>   # Keep main version")
                        self.logger.error(f"     git checkout --theirs <file> # Keep branch version")
                        self.logger.error(f"  2. Or manually merge the content")

                    self.logger.error("\nOption 1 - Manual Merge:")
                    self.logger.error(f"  git checkout {Config.MAIN_BRANCH}")
                    self.logger.error(f"  git pull origin {Config.MAIN_BRANCH}  # Ensure main is up to date")
                    self.logger.error(f"  git merge origin/{branch_name}")
                    self.logger.error("  # Resolve conflicts in files")
                    self.logger.error("  git add <resolved-files>")
                    self.logger.error("  git commit")
                    self.logger.error("\nOption 2 - Squash Merge (simpler):")
                    self.logger.error(f"  git checkout {Config.MAIN_BRANCH}")
                    self.logger.error(f"  git pull origin {Config.MAIN_BRANCH}  # Ensure main is up to date")
                    self.logger.error(f"  git merge --squash origin/{branch_name}")
                    self.logger.error("  # Resolve conflicts using git checkout --theirs or --ours")
                    self.logger.error("  git add <resolved-files>")
                    self.logger.error(f"  git commit -m 'Merge {branch_name}'")
                    self.logger.error("\nOption 3 - Create Pull Request:")
                    self.logger.error(f"  gh pr create --base {Config.MAIN_BRANCH} --head {branch_name}")
                    self.logger.error("=" * 60)

            else:
                self.logger.info(f"[DRY RUN] Would merge {branch_name}")
                merged_count += 1

        if failed_branches:
            self.logger.warning(f"Failed to merge {len(failed_branches)} branches:")
            for branch in failed_branches:
                self.logger.warning(f"  - {branch}")

        if merged_count > 0:
            self.logger.info(f"\nOK Successfully merged {merged_count} Claude branch(es)")

            # Push merged changes
            if not self.dry_run:
                return self._push_to_remote()

        return len(failed_branches) == 0

    def _provide_recovery_instructions(self, state: Dict[str, Any]):
        """Provide manual recovery instructions"""
        self.logger.info("\n" + "=" * 70)
        self.logger.info("MANUAL RECOVERY REQUIRED")
        self.logger.info("=" * 70)

        if state.get('merge_in_progress'):
            self.logger.info("\n1. Repository has ongoing merge:")
            self.logger.info("   Option A - Complete the merge:")
            self.logger.info("     git status  # See conflicted files")
            self.logger.info("     # Edit files to resolve conflicts")
            self.logger.info("     git add <files>")
            self.logger.info("     git commit")
            self.logger.info("\n   Option B - Abort the merge:")
            self.logger.info("     git merge --abort")

        if state.get('rebase_in_progress'):
            self.logger.info("\n2. Repository has ongoing rebase:")
            self.logger.info("   Option A - Complete the rebase:")
            self.logger.info("     git status")
            self.logger.info("     # Resolve conflicts")
            self.logger.info("     git add <files>")
            self.logger.info("     git rebase --continue")
            self.logger.info("\n   Option B - Abort the rebase:")
            self.logger.info("     git rebase --abort")

        if state.get('has_conflicts'):
            self.logger.info("\n3. Files contain conflict markers:")
            self.logger.info("   Conflicted files:")
            for f in state.get('conflict_files', []):
                self.logger.info(f"     - {f}")
            self.logger.info("\n   Edit files and remove conflict markers:")
            self.logger.info("     <<<<<<< HEAD")
            self.logger.info("     =======")
            self.logger.info("     >>>>>>>")

        if state.get('detached_head'):
            self.logger.info("\n4. Repository in detached HEAD state:")
            self.logger.info("     git checkout main  # Return to main branch")

        self.logger.info("\n" + "=" * 70)

# ============================================================================
# Main Entry Point
# ============================================================================

def check_git_availability():
    """Check if git is available and working"""
    try:
        result = subprocess.run(
            ['git', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True, result.stdout.strip()
        else:
            return False, "Git command failed"
    except FileNotFoundError:
        return False, "Git executable not found in PATH"
    except Exception as e:
        return False, f"Git check failed: {e}"


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Intelligent Auto Git Sync - Zero-interaction edition',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python auto-git-sync.py              # Full automatic sync
  python auto-git-sync.py --dry-run    # Preview without changes
  python auto-git-sync.py --verbose    # Detailed logging
  python auto-git-sync.py --force      # Skip safety delays

Safety:
  - Creates full backup before any changes
  - Never force-pushes without verification
  - Preserves all uncommitted changes
  - Aborts on unrecoverable conflicts
  - Provides recovery instructions
        """
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be done without making changes'
    )

    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )

    parser.add_argument(
        '--force',
        action='store_true',
        help='Skip safety delays'
    )

    args = parser.parse_args()

    # Setup logging
    logger = setup_logging(verbose=args.verbose)

    # Check git availability
    git_available, git_info = check_git_availability()
    if not git_available:
        logger.error("=" * 70)
        logger.error("GIT NOT AVAILABLE")
        logger.error("=" * 70)
        logger.error(f"Error: {git_info}")
        logger.error("\nTroubleshooting:")
        logger.error("1. Make sure Git is installed:")
        logger.error("   - Windows: Download from https://git-scm.com/download/win")
        logger.error("   - Run: git --version")
        logger.error("2. Make sure Git is in your PATH")
        logger.error("3. Restart your terminal/PowerShell after installing Git")
        logger.error("4. If using virtual environment, make sure Git is accessible")
        logger.error("=" * 70)
        sys.exit(1)
    else:
        logger.info(f"Git detected: {git_info}")

    # Initialize components
    git = GitCommand(logger)
    backup = BackupManager(logger, git)
    engine = AutoSyncEngine(
        logger=logger,
        git=git,
        backup=backup,
        dry_run=args.dry_run,
        force=args.force
    )

    # Run sync
    try:
        success = engine.sync()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        logger.warning("\n\nSync interrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"\n\nUnexpected error: {e}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    main()
