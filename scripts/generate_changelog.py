#!/usr/bin/env python
# Copyright 2023-2024 ByteBrain AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
