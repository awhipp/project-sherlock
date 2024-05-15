"""Python script to analyze git history and determine version bump."""

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
    commit_messages = result.stdout.decode("utf-8").split("\n")

    valid_commit_messages = []

    for message in commit_messages:
        if "Merge pull request" in message:
            break
        valid_commit_messages.append(message)

    return valid_commit_messages


if __name__ == "__main__":
    # Get commit messages
    get_commit_messages = get_commit_messages()

    # Output new line separated commit messages
    print("\n".join(get_commit_messages))
