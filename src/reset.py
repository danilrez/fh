#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

#############################################
#               USER CONFIG                #
#############################################

TARGET_YEAR = 2025  # The year for which commits will be removed
REMOTE_URL  = "https://github.com/danilrez/fh"  # Your repository URL
BRANCH      = "main"  # Target branch

#############################################
#         UTILITY FUNCTIONS                #
#############################################

def run_cmd(cmd: str) -> None:
    """
    Runs a shell command. Exits if the command fails.
    """
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed:\n{cmd}\nError: {e}")
        sys.exit(1)

def is_workdir_clean() -> bool:
    """
    Returns True if 'git status --porcelain' is empty (i.e., no uncommitted changes).
    """
    result = subprocess.run(["git", "status", "--porcelain"],
                            stdout=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

#############################################
#          BUILD FILTER SCRIPT             #
#############################################

# Define start and end datetime for the target year.
start_dt = datetime(TARGET_YEAR, 1, 1, 0, 0, 0)
end_dt   = datetime(TARGET_YEAR, 12, 31, 23, 59, 59)

start_ts = int(start_dt.timestamp())
end_ts   = int(end_dt.timestamp())

# Inline Python snippet to be run by python3 -c.
# Note: We double the '%' signs in the format strings to avoid shell interpolation issues.
inline_python = (
    "import os, sys; from datetime import datetime; "
    f"start_ts={start_ts}; end_ts={end_ts}; "
    "raw = os.environ.get('GIT_AUTHOR_DATE','').strip(); "
    "fmt_tz='%%a %%b %%d %%H:%%M:%%S %%Y %%z'; "
    "fmt_no_tz='%%a %%b %%d %%H:%%M:%%S %%Y'; "
    "try: dt = datetime.strptime(raw, fmt_tz) "
    "except ValueError: dt = datetime.strptime(raw[:-6], fmt_no_tz) "
    "ts = int(dt.timestamp()); "
    "sys.exit(0 if start_ts <= ts <= end_ts else 1)"
)

# Build the git filter-branch command using the inline Python snippet.
filter_branch_cmd = f"""
git filter-branch --force --commit-filter '
TS=$(python3 -c "{inline_python}")
if [ "$TS" -eq 0 ]; then
    skip_commit "$@"
else
    git commit-tree "$@"
fi
' -- --all
"""

#############################################
#               MAIN SCRIPT                #
#############################################

def main():
    print(f"WARNING: This will rewrite your git history by removing all commits for the year {TARGET_YEAR}.")
    print("Make sure you have a backup of your repository.")

    # Check that the working directory is clean.
    if not is_workdir_clean():
        print("[ERROR] Your working directory has uncommitted changes. Please commit or stash them first.")
        sys.exit(1)

    confirm = input(f"Are you sure you want to remove commits from {TARGET_YEAR}? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        sys.exit(0)

    print(f"Removing commits dated between {start_dt} and {end_dt} ...")
    print("Rewriting history (this may take a while)...")

    run_cmd(filter_branch_cmd)

    # Cleanup: remove backup refs and run garbage collection.
    run_cmd("rm -rf .git/refs/original/")
    run_cmd("git reflog expire --expire=now --all")
    run_cmd("git gc --prune=now --aggressive")

    print(f"\nHistory for {TARGET_YEAR} has been rewritten locally. All commits from {TARGET_YEAR} have been removed.")

    # Force push new history to remote.
    confirm_push = input("Do you want to force push the new history to the remote repository? (yes/no): ")
    if confirm_push.lower() == "yes":
        run_cmd(f"git branch -M {BRANCH}")
        run_cmd(f"git remote add origin {REMOTE_URL} || echo 'Remote already exists'")
        run_cmd(f"git push -f origin {BRANCH}")
        print("Force push complete. Remote history has been overwritten.")
    else:
        print("Local history has been rewritten. Remember to push manually if needed.")

if __name__ == "__main__":
    main()