import os
import random
import sys
from datetime import datetime, timedelta
from dotenv import load_dotenv
from helpers import (
    run_cmd,
    print_progress_bar,
    check_repo_clean,
    COLOR_BOLD,
    COLOR_BG_RED,
    COLOR_RESET,
    COLOR_RED,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_BLUE
)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), ".env"))

#############################################
#               USER CONFIG                #
#############################################

REPO_URL = os.getenv("REPO_URL")               # e.g., "https://github.com/danilrez/fh"
BRANCH_NAME = os.getenv("BRANCH_NAME")         # e.g., "main"
TARGET_YEAR = int(os.getenv("TARGET_YEAR", "2024"))
MIN_COMMITS_PER_DAY = int(os.getenv("MIN_COMMITS_PER_DAY", "1"))
MAX_COMMITS_PER_DAY = int(os.getenv("MAX_COMMITS_PER_DAY", "3"))

#############################################
#               STATIC CONFIG              #
#############################################

# We'll create commits from Jan 1 (inclusive) to Dec 31 (exclusive)
start_date = datetime(TARGET_YEAR, 1, 1)
end_date   = datetime(TARGET_YEAR, 12, 31)  # Not included in the loop

# File for fake commits (stored in src/commit_log.txt)
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMIT_FILE = os.path.join(repo_root, "src", "commit_log.txt")

#############################################
#                MAIN SCRIPT               #
#############################################

if __name__ == "__main__":
    # Move to the repo root (one level above src/)
    os.chdir(repo_root)

    # If not a Git repo, initialize one
    if not os.path.exists(".git"):
        run_cmd("git init")

    # Check if repository is clean before proceeding
    check_repo_clean()

    # Pull the latest changes quietly (no "Already up to date." message)
    run_cmd(f"git pull --quiet origin {BRANCH_NAME} --rebase")

    # Calculate total days in the range
    total_days = (end_date - start_date).days
    if total_days <= 0:
        print(f"{COLOR_BOLD}{COLOR_BG_RED}[ERROR]{COLOR_RESET} {COLOR_RED}Invalid date range: start={start_date.date()} end={end_date.date()}{COLOR_RESET}")
        sys.exit(1)

    # Print start message (using CYAN color)
    print(f"\n{COLOR_CYAN}Starting commit generation for {COLOR_BOLD}{TARGET_YEAR}...{COLOR_RESET}\n")

    current_date = start_date
    day_counter = 0

    while current_date < end_date:
        # Generate a random number of commits for this day
        num_commits = random.randint(MIN_COMMITS_PER_DAY, MAX_COMMITS_PER_DAY)

        for _ in range(num_commits):
            hour = random.randint(0, 23)
            minute = random.randint(0, 59)
            commit_dt = datetime(current_date.year, current_date.month, current_date.day, hour, minute, 0)
            commit_date_str = commit_dt.strftime('%Y-%m-%dT%H:%M:%S')

            with open(COMMIT_FILE, "a") as f:
                f.write(f"Commit from {commit_date_str}\n")

            run_cmd(f'git add "{COMMIT_FILE}"')
            run_cmd(
                f'GIT_AUTHOR_DATE="{commit_date_str}" '
                f'GIT_COMMITTER_DATE="{commit_date_str}" '
                f'git commit -m "Commit from {commit_date_str}"'
            )

        day_counter += 1
        print_progress_bar(day_counter, total_days, prefix="Progress", suffix="Complete")
        current_date += timedelta(days=1)

    # Cleanup logs
    with open(COMMIT_FILE, "w") as f:
        pass

    # Rename branch and push changes quietly
    run_cmd(f"git branch -M {BRANCH_NAME}")

    # Check if remote 'origin' already exists; if not, add it
    existing_remote = os.popen("git remote get-url origin").read().strip()
    if not existing_remote:
        run_cmd(f"git remote add origin {REPO_URL}")

    run_cmd(f"git push origin {BRANCH_NAME}")

    # Print final message
    print(f"\n{COLOR_BOLD}{COLOR_GREEN}[Done]{COLOR_RESET} "
          f"{COLOR_GREEN}All commits have been pushed to: {COLOR_RESET}{COLOR_YELLOW}{REPO_URL}"
          f"{COLOR_BLUE}({BRANCH_NAME}){COLOR_RESET}")