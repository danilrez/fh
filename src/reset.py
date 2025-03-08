#!/usr/bin/env python3
import os
import sys
import subprocess
from datetime import datetime

#############################################
#               USER CONFIG                #
#############################################

TARGET_YEAR = 2024  # Year to remove
REMOTE_URL  = "https://github.com/danilrez/fh"
BRANCH      = "main"

#############################################
#        UTILITY & HELPER FUNCTIONS        #
#############################################

def run_cmd(cmd: str) -> None:
    """
    Runs a shell command. Exits on failure.
    """
    try:
        subprocess.run(cmd, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"\n[ERROR] Command failed:\n{cmd}\n{e}")
        sys.exit(1)

def is_workdir_clean() -> bool:
    """
    Returns True if 'git status --porcelain' is empty, meaning no uncommitted changes.
    """
    result = subprocess.run(["git", "status", "--porcelain"],
                            stdout=subprocess.PIPE, text=True)
    return len(result.stdout.strip()) == 0

#############################################
#              BUILD FILTER CMD            #
#############################################

"""
We define a Python one-liner that checks if $GIT_AUTHOR_DATE
falls within the target year's timestamp range. If yes => skip_commit,
otherwise => keep the commit.

This approach avoids 'date --date' usage, which is problematic on macOS.
"""

start_dt = datetime(TARGET_YEAR, 1, 1, 0, 0, 0)
end_dt   = datetime(TARGET_YEAR, 12, 31, 23, 59, 59)
start_ts = int(start_dt.timestamp())
end_ts   = int(end_dt.timestamp())

# One-liner in Python that:
# - reads GIT_AUTHOR_DATE from environment
# - parses with or without timezone
# - exits(0) if date in [start_ts..end_ts], else exits(1)
inline_python = (
    "import os, sys; from datetime import datetime; "
    f"start_ts={start_ts}; end_ts={end_ts}; "
    "raw = os.environ.get('GIT_AUTHOR_DATE','').strip(); "
    "fmt_tz='%a %b %d %H:%M:%S %Y %z'; "
    "fmt_no_tz='%a %b %d %H:%M:%S %Y'; "
    "try: dt=datetime.strptime(raw,fmt_tz) "
    "except ValueError: dt=datetime.strptime(raw[:-6],fmt_no_tz) "
    "ts=int(dt.timestamp()); "
    "sys.exit(0 if start_ts<=ts<=end_ts else 1)"
)

# We embed this snippet into the filter-branch commit-filter:
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
#                 MAIN SCRIPT              #
#############################################

def main():
    print(f"\nThis script will REMOVE all commits dated in {TARGET_YEAR}.")
    print("It uses 'git filter-branch', which rewrites history.")
    print("Make sure you have a backup. Press Ctrl-C to abort now.\n")

    # 1) Check if workdir is clean
    if not is_workdir_clean():
        print("[ERROR] Your working directory has uncommitted changes. Please commit or stash them first.")
        sys.exit(1)

    # 2) Confirm
    confirm = input(f"Are you sure you want to remove commits from {TARGET_YEAR}? (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        sys.exit(0)

    print(f"Removing commits with dates between {start_dt} and {end_dt} ...")

    # 3) Run filter-branch
    print("Rewriting history (this may take a while)...")
    run_cmd(filter_branch_cmd)

    # 4) Cleanup
    run_cmd("rm -rf .git/refs/original/")
    run_cmd("git reflog expire --expire=now --all")
    run_cmd("git gc --prune=now --aggressive")

    print(f"\nAll commits from {TARGET_YEAR} have been removed LOCALLY.")

    # 5) Optional force push
    confirm_push = input("Do you want to FORCE push the new history to remote? (yes/no): ")
    if confirm_push.lower() == "yes":
        run_cmd(f"git branch -M {BRANCH}")
        run_cmd(f"git remote add origin {REMOTE_URL} || echo 'Remote already exists'")
        run_cmd(f"git push -f origin {BRANCH}")
        print("Force push complete. Remote history overwritten.")
    else:
        print("Local rewrite done. Remember to push (force) if you want to update remote.\n")

if __name__ == "__main__":
    main()