#!/usr/bin/env python
import subprocess
import sys


def generate_changelog(old_commit, new_commit):
    try:
        # Get the commit messages between the old and new commits
        git_log_command = f"git log --oneline {old_commit}..{new_commit} --pretty=format:'%h %s'"
        commit_messages = subprocess.check_output(git_log_command, shell=True, text=True)

        # Generate the changelog
        changelog = f"Changelog from {old_commit} to {new_commit}:\n\n{commit_messages}"

        return changelog
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return None


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: generate_changelog.py <old_commit> <new_commit>")
        sys.exit(1)

    old_commit = sys.argv[1]
    new_commit = sys.argv[2]

    changelog = generate_changelog(old_commit, new_commit)

    if changelog:
        print(changelog)
    else:
        sys.exit(1)
