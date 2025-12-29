"""
Server Angel Git Watcher Module
Monitors GitHub branch for new commits and triggers deployments.
"""

import subprocess
import os
import logging
from pathlib import Path
from config import Config


class GitWatcher:
    """Handles Git repository monitoring and commit detection."""

    @staticmethod
    def get_current_commit():
        """Get current commit hash from the repository."""
        try:
            os.chdir(Config.PROJECT_ROOT)

            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                return result.stdout.strip()
            else:
                raise Exception(f"Git command failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to get current commit: {str(e)}")

    @staticmethod
    def get_last_deployed_commit():
        """Get the last deployed commit hash from state file."""
        try:
            if Config.LAST_COMMIT_FILE.exists():
                with open(Config.LAST_COMMIT_FILE, 'r') as f:
                    return f.read().strip()
            else:
                # If no state file exists, get current commit and save it
                current = GitWatcher.get_current_commit()
                GitWatcher.save_last_deployed_commit(current)
                return current

        except Exception as e:
            raise Exception(f"Failed to read last deployed commit: {str(e)}")

    @staticmethod
    def save_last_deployed_commit(commit_hash):
        """Save the last deployed commit hash to state file."""
        try:
            Config.LAST_COMMIT_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(Config.LAST_COMMIT_FILE, 'w') as f:
                f.write(commit_hash)
        except Exception as e:
            raise Exception(f"Failed to save last deployed commit: {str(e)}")

    @staticmethod
    def fetch_remote():
        """Fetch latest changes from remote repository."""
        try:
            os.chdir(Config.PROJECT_ROOT)
            logging.info(f"Fetching from remote: {Config.GIT_REMOTE}")

            result = subprocess.run(
                ['git', 'fetch', Config.GIT_REMOTE],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                logging.error(f"Git fetch failed: {result.stderr}")
                raise Exception(f"Git fetch failed: {result.stderr}")

            logging.info("Successfully fetched from remote")

        except subprocess.TimeoutExpired:
            logging.error("Git fetch timed out after 60 seconds")
            raise Exception("Git fetch timed out")
        except Exception as e:
            raise Exception(f"Failed to fetch from remote: {str(e)}")

    @staticmethod
    def check_for_new_commits():
        """Check if there are new commits on the production branch."""
        try:
            # Fetch latest changes
            GitWatcher.fetch_remote()

            # Get last deployed commit
            last_deployed = GitWatcher.get_last_deployed_commit()

            # Check if remote branch has new commits
            os.chdir(Config.PROJECT_ROOT)

            result = subprocess.run(
                ['git', 'rev-list', f'{last_deployed}..{Config.GIT_REMOTE}/{Config.GIT_BRANCH}'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                new_commits = result.stdout.strip().split('\n')
                new_commits = [c for c in new_commits if c]  # Remove empty strings

                if new_commits:
                    latest_commit = new_commits[0]  # Most recent commit
                    return {
                        'new_commits': True,
                        'commit_hash': latest_commit,
                        'commit_count': len(new_commits)
                    }
                else:
                    return {
                        'new_commits': False,
                        'message': 'No new commits detected'
                    }
            else:
                raise Exception(f"Git rev-list failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to check for new commits: {str(e)}")

    @staticmethod
    def check_requirements_changed():
        """Check if requirements.txt has changed since last deployment."""
        try:
            os.chdir(Config.PROJECT_ROOT)

            # Get last deployed commit
            last_deployed = GitWatcher.get_last_deployed_commit()

            # Check if requirements.txt changed
            result = subprocess.run(
                ['git', 'diff', '--name-only', last_deployed, 'HEAD', 'requirements.txt'],
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                changed_files = result.stdout.strip().split('\n')
                changed_files = [f for f in changed_files if f]  # Remove empty strings

                return 'requirements.txt' in changed_files
            else:
                raise Exception(f"Git diff failed: {result.stderr}")

        except Exception as e:
            raise Exception(f"Failed to check requirements changes: {str(e)}")

    @staticmethod
    def run_watch_cycle():
        """Run complete watch cycle for new commits."""
        try:
            result = GitWatcher.check_for_new_commits()

            if result.get('new_commits', False):
                # Check if requirements changed
                requirements_changed = GitWatcher.check_requirements_changed()

                return {
                    'trigger_deployment': True,
                    'commit_hash': result['commit_hash'],
                    'commit_count': result['commit_count'],
                    'requirements_changed': requirements_changed
                }
            else:
                return {
                    'trigger_deployment': False,
                    'message': result.get('message', 'No changes detected')
                }

        except Exception as e:
            raise Exception(f"Watch cycle failed: {str(e)}")
