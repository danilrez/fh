import os
import sys
import random
from datetime import datetime, timedelta

#############################################
#               USER CONFIG                #
#############################################

REPO_URL = "https://github.com/danilrez/fh"  # Your repository URL
BRANCH_NAME = "main"                         # Target branch
TARGET_YEAR = 2023                           # Target year for commits
COMMITS_PER_X = 15                           # Number of commits per 'X'

#############################################
#               STATIC CONFIG              #
#############################################

# We'll store the dummy commits in src/commit_log.txt
COMMIT_FILE = "src/commit_log.txt"

# Reference date: Dec 31 of the previous year
ref_date = datetime(TARGET_YEAR - 1, 12, 31)

# Offsets to align each year. Adjust as needed.
year_offsets = {2025: 33, 2024: 35, 2023: 36, 2022: 30, 2021: 31, 2020: 33}
year_offset = year_offsets.get(TARGET_YEAR, 35)
letter_offset = year_offset

#############################################
#             COLOR & STYLES               #
#############################################

COLOR_RESET        = "\033[0m"
COLOR_CYAN         = "\033[96m"
COLOR_GREEN        = "\033[32m"
COLOR_YELLOW       = "\033[33m"
COLOR_BRIGHT_GREEN = "\033[92m"
COLOR_BOLD         = "\033[1m"
COLOR_RED          = "\033[31m"
COLOR_BG_RED       = "\033[41m"
COLOR_BLUE         = "\033[34m"

#############################################
#            UTILITY FUNCTIONS             #
#############################################

def run_cmd(cmd: str) -> None:
    """Runs a shell command quietly (redirecting output to /dev/null)."""
    os.system(f"{cmd} > /dev/null 2>&1")

def print_progress_bar(iteration: int, total: int, prefix: str = '', suffix: str = '', length: int = 40) -> None:
    """
    Prints/updates a unified progress bar in one line.
    The percentage is shown in plain green.
    """
    if iteration > total:
        iteration = total
    percent = 100.0 * iteration / float(total)
    filled_length = int(length * iteration // total)
    bar = (COLOR_BRIGHT_GREEN + '█' * filled_length + COLOR_RESET +
           '-' * (length - filled_length))
    sys.stdout.write(f'\r{prefix} |{bar}| {COLOR_GREEN}{percent:5.1f}%{COLOR_RESET} {suffix}')
    sys.stdout.flush()
    if iteration >= total:
        sys.stdout.write('\n\n')
        sys.stdout.flush()

#############################################
#               MAIN SCRIPT                #
#############################################

# Each character is defined as a dict with:
#  - "char": the letter (or "SPACE")
#  - "pattern": 7 strings for rows (4 columns for most letters, 5 for M/V)
#  - "offset": number of days to move after finishing a letter

letters = [
    {
        "char": "G",
        "pattern": [
            " XX ",
            "X  X",
            "X   ",
            "X XX",
            "X  X",
            "X  X",
            " XX "
        ],
        "offset": 35
    },
    {
        "char": "A",
        "pattern": [
            " XX ",
            "X  X",
            "X  X",
            "XXXX",
            "X  X",
            "X  X",
            "X  X"
        ],
        "offset": 35
    },
    {
        "char": "M",
        "pattern": [
            "X   X",
            "XX XX",
            "X X X",
            "X X X",
            "X   X",
            "X   X",
            "X   X"
        ],
        "offset": 42
    },
    {
        "char": "E",
        "pattern": [
            "XXXX",
            "X   ",
            "X   ",
            "XXX ",
            "X   ",
            "X   ",
            "XXXX"
        ],
        "offset": 35
    },
    {
        "char": "SPACE",
        "pattern": [],
        "offset": 7
    },
    {
        "char": "O",
        "pattern": [
            " XX ",
            "X  X",
            "X  X",
            "X  X",
            "X  X",
            "X  X",
            " XX "
        ],
        "offset": 35
    },
    {
        "char": "V",
        "pattern": [
            "X   X",
            "X   X",
            "X   X",
            "X   X",
            "X   X",
            " X X ",
            "  X  "
        ],
        "offset": 42
    },
    {
        "char": "E",
        "pattern": [
            "XXXX",
            "X   ",
            "X   ",
            "XXX ",
            "X   ",
            "X   ",
            "XXXX"
        ],
        "offset": 35
    },
    {
        "char": "R",
        "pattern": [
            "XXX ",
            "X  X",
            "X  X",
            "XXX ",
            "X X ",
            "X  X",
            "X  X"
        ],
        "offset": 35
    }
]

# Calculate total commits to be made (COMMITS_PER_X for each 'X' in all patterns)
total_commits = sum(
    sum(COMMITS_PER_X for ch in row if ch == 'X')
    for letter in letters
    for row in letter["pattern"]
)
commits_done = 0

# Initial message
print(f"\n{COLOR_BOLD}{COLOR_CYAN}Starting commit generation for {TARGET_YEAR}...{COLOR_RESET}")
print(f"{COLOR_BOLD}ref_date = {ref_date.date()}, year_offset = {year_offset}{COLOR_RESET}\n")

for letter in letters:
    if letter["char"] == "SPACE":
        letter_offset += letter["offset"]
        continue

    for row, line in enumerate(letter["pattern"]):
        for col, ch in enumerate(line):
            if ch == 'X':
                # Calculate day_index relative to current letter offset
                day_index = letter_offset + col * 7 + row
                current_date = ref_date + timedelta(days=day_index)
                for _ in range(COMMITS_PER_X):
                    commit_date_str = current_date.strftime("%Y-%m-%dT%H:%M:%S")
                    with open(COMMIT_FILE, "a") as f:
                        f.write(f"{letter['char']} letter commit {commit_date_str}\n")
                    run_cmd(f'git add "{COMMIT_FILE}"')
                    run_cmd(
                        f'GIT_AUTHOR_DATE="{commit_date_str}" '
                        f'GIT_COMMITTER_DATE="{commit_date_str}" '
                        f'git commit -m "{letter["char"]} letter commit {commit_date_str}"'
                    )
                    commits_done += 1
                    print_progress_bar(commits_done, total_commits, prefix="Progress", suffix="Complete")
    letter_offset += letter["offset"]

print("\nPushing commits to remote repository...\n")
run_cmd(f"git push -f origin {BRANCH_NAME}")

print(
    f"{COLOR_BOLD}{COLOR_GREEN}[Done]{COLOR_RESET} "
    f"{COLOR_GREEN}All commits have been pushed to: {COLOR_RESET}{COLOR_YELLOW}{REPO_URL} "
    f"{COLOR_BLUE}(branch: {BRANCH_NAME}){COLOR_RESET}\n"
)