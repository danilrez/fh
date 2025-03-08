import os
import sys
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from helpers import (
    run_cmd,
    print_progress_bar,
    check_repo_clean,
    COLOR_BOLD,
    COLOR_CYAN,
    COLOR_GREEN,
    COLOR_YELLOW,
    COLOR_BLUE,
    COLOR_RESET
)

# Load environment variables from .env file in project root
load_dotenv(os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), ".env"))

#############################################
#               USER CONFIG                #
#############################################

REPO_URL = os.getenv("REPO_URL")               # e.g., "https://github.com/danilrez/fh"
BRANCH_NAME = os.getenv("BRANCH_NAME")         # e.g., "main"
TARGET_YEAR = int(os.getenv("TARGET_YEAR", "2024"))
COMMITS_PER_X = int(os.getenv("COMMITS_PER_X", "5"))

#############################################
#               STATIC CONFIG              #
#############################################

# File for fake commits (stored in src/commit_log.txt)
# Script is in src/, so repo_root = ".." from here.
repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
COMMIT_FILE = os.path.join(repo_root, "src", "commit_log.txt")

# Reference date: Dec 31 of the previous year
ref_date = datetime(TARGET_YEAR - 1, 12, 31)

# Offsets to align each year. Adjust as needed.
year_offsets = {2025: 33, 2024: 35, 2023: 36, 2022: 30, 2021: 31, 2020: 33}
year_offset = year_offsets.get(TARGET_YEAR, 35)
letter_offset = year_offset

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


# Check if repository is clean before proceeding
check_repo_clean()

# Calculate total commits to be made (COMMITS_PER_X for each 'X' in all patterns)
total_commits = sum(
    sum(COMMITS_PER_X for ch in row if ch == 'X')
    for letter in letters
    for row in letter["pattern"]
)
commits_done = 0

# Initial message
print(f"\n{COLOR_CYAN}Starting commit generation for {COLOR_BOLD}{TARGET_YEAR}...{COLOR_RESET}")

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

# Cleanup logs
with open(COMMIT_FILE, "w") as f:
    pass

print("Pushing commits to remote repository...\n")
run_cmd(f"git push -f origin {BRANCH_NAME}")

print(
    f"{COLOR_BOLD}{COLOR_GREEN}[Done]{COLOR_RESET} "
    f"{COLOR_GREEN}All commits have been pushed to: {COLOR_RESET}{COLOR_YELLOW}{REPO_URL}"
    f"{COLOR_BLUE}({BRANCH_NAME}){COLOR_RESET}"
)