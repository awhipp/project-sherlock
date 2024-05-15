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

    number_merges = 0

    for message in commit_messages:
        if "Merge pull request" in message:
            number_merges += 1
            if number_merges > 1:
                break
        if number_merges == 1 and "Merge pull request" not in message:
            valid_commit_messages.append(message)

    return valid_commit_messages


if __name__ == "__main__":
    # Get commit messages
    get_commit_messages = get_commit_messages()

    # Output new line separated commit messages
    print("\n".join(get_commit_messages))
