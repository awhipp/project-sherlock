# analyze_commits.py
import subprocess


def get_commit_messages():
    """Get the commit messages from the current branch.

    Returns:
        list: A list of commit messages.
    """
    result = subprocess.run(
        ["git", "log", "--pretty=format:%s"],
        stdout=subprocess.PIPE,
        check=True,
    )
    return result.stdout.decode("utf-8").split("\n")


def analyze_commit_messages(messages):
    """Analyze commit messages to determine the next version bump.

    Args:
        messages (list): A list of commit messages.

    Returns:
        str: The version bump type (major, minor, patch) or None if no bump is needed.
    """
    maximal_bump = "None"
    number_merges = 0
    for message in messages:
        if message.startswith("fix:") and maximal_bump in ["None", "patch"]:
            maximal_bump = "patch"
        elif message.startswith("feat:") and maximal_bump in ["None", "patch", "minor"]:
            maximal_bump = "minor"
        elif "BREAKING CHANGE" in message and maximal_bump in [
            "None",
            "patch",
            "minor",
            "major",
        ]:
            maximal_bump = "major"
        elif "Merge pull request" in message:
            number_merges += 1
            if number_merges > 1:
                return maximal_bump
    return "None"


def main():
    """Analyze commit messages and determine the next version bump."""
    messages = get_commit_messages()
    bump = analyze_commit_messages(messages)
    print(bump)


if __name__ == "__main__":
    main()
