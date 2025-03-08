import os
import sys

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
    """
    Runs a shell command, redirecting stdout and stderr to /dev/null.
    """
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
