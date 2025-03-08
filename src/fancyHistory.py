import os
import random
import sys
from datetime import datetime, timedelta

#############################################
#               CONFIG SECTION             #
#############################################

TARGET_YEAR = 2023
BRANCH_NAME = "main"
REPO_URL  = "https://github.com/danilrez/fh"

# We'll create commits from Jan 1 (inclusive) to Dec 31 (exclusive)
start_date = datetime(TARGET_YEAR, 1, 1)
end_date   = datetime(TARGET_YEAR, 12, 31)  # Not included in the loop

# Range of commits per day
MIN_COMMITS_PER_DAY = 1
MAX_COMMITS_PER_DAY = 1

# File for fake commits (stored in src/commit_log.txt)
# Script is in src/, so repo_root = ".." from here.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMIT_FILE = os.path.join(repo_root, "src", "commit_log.txt")

#############################################
#             COLOR & STYLES               #
#############################################

COLOR_RESET         = "\033[0m"
COLOR_CYAN          = "\033[96m"
COLOR_GREEN         = "\033[32m"
COLOR_YELLOW        = "\033[33m"
COLOR_BRIGHT_GREEN  = "\033[92m"
COLOR_BOLD          = "\033[1m"
COLOR_RED           = "\033[31m"
COLOR_BG_RED        = "\033[41m"
COLOR_BLUE          = "\033[34m"

#############################################
#            UTILITY FUNCTIONS             #
#############################################

def run_cmd(cmd: str) -> None:
    """
    Runs a shell command, redirecting stdout and stderr to /dev/null.
    """
    os.system(f"{cmd} > /dev/null 2>&1")

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 40) -> None:
    """
    Print/update a progress bar in the console (in one line).
    The percentage text is printed in green.
    """
    percent = 100 * (iteration / float(total))
    filled_length = int(length * iteration // total)
    bar = (COLOR_BRIGHT_GREEN + '█' * filled_length + COLOR_RESET +
           '-' * (length - filled_length))
    # Print percentage in plain green
    sys.stdout.write(f'\r{prefix} |{bar}| {COLOR_GREEN}{percent:5.1f}%{COLOR_RESET} {suffix}')
    sys.stdout.flush()
    if iteration == total:
        print()

def check_repo_clean() -> None:
    """
    Checks if there are uncommitted changes.
    If so, prints an error message with red background and red text and exits.
    """
    status = os.popen("git status --porcelain").read().strip()
    if status:
        error_msg = (f"{COLOR_BOLD}{COLOR_BG_RED}{COLOR_RED}[ERROR]{COLOR_RESET} "
                     f"{COLOR_RED}Please commit or stash them.{COLOR_RESET}")
        print(error_msg)
        sys.exit(1)

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

    # Pull the latest changes quietly to avoid conflicts
    run_cmd(f"git pull origin {BRANCH_NAME} --rebase || echo 'No remote changes to pull'")

    # Calculate total days in the range
    total_days = (end_date - start_date).days
    if total_days <= 0:
        print(f"{COLOR_BOLD}{COLOR_BG_RED}[ERROR]{COLOR_RESET} {COLOR_RED}Invalid date range: start={start_date.date()} end={end_date.date()}{COLOR_RESET}")
        sys.exit(1)

    # Print start message (using CYAN color)
    print(f"{COLOR_BOLD}{COLOR_CYAN}Starting commit generation for {TARGET_YEAR}...{COLOR_RESET}")

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

    # Rename branch and push changes quietly
    run_cmd(f"git branch -M {BRANCH_NAME}")

    # Check if remote 'origin' already exists; if not, add it.
    existing_remote = os.popen("git remote get-url origin").read().strip()
    if not existing_remote:
        run_cmd(f"git remote add origin {REPO_URL}")

    run_cmd(f"git push origin {BRANCH_NAME}")

    # Print final message with bold green "[Done]" and green text for the rest
    print(f"{COLOR_BOLD}{COLOR_GREEN}[Done]{COLOR_RESET} {COLOR_GREEN}All commits have been pushed to: {COLOR_RESET}{COLOR_YELLOW}{REPO_URL} {COLOR_BLUE}(branch: {BRANCH_NAME}){COLOR_RESET}\n")