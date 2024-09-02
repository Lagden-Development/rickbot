"""
(c) 2024 Lagden Development (All Rights Reserved)
Licensed for non-commercial use with attribution required; provided 'as is' without warranty.
See https://github.com/Lagden-Development/.github/blob/main/LICENSE for more information.

This helper provides a function which generates an embed with the latest updates (commits) from a GitHub repository.
"""

# Python Standard Library
# ------------------------
from datetime import (
    datetime,
)  # Used for parsing and formatting date and time information.

# Third Party Libraries
# ---------------------
from discord_timestamps import (
    format_timestamp,
    TimestampType,
)  # Helps format timestamps for Discord messages.
import discord  # Core library for interacting with Discord's API
import requests  # Handles HTTP requests.

# Internal Modules
# ----------------
from helpers.colors import (
    MAIN_EMBED_COLOR,
)  # Predefined color constant for Discord embeds.

# Config
# ------
from config import CONFIG  # Imports the bot's configuration settings.


# Custom Exceptions
class InvalidGitHubURL(Exception):
    """
    Exception raised when an invalid GitHub URL is encountered.

    Attributes:
    message (str): The error message explaining the issue.
    """

    def __init__(self, message: str = "Invalid GitHub URL"):
        self.message = message
        super().__init__(self.message)


class GithubApiError(Exception):
    """
    Exception raised when an error occurs while interacting with the GitHub API.

    Attributes:
    message (str): The error message explaining the issue.
    """

    def __init__(
        self, message: str = "An error occurred while interacting with the GitHub API"
    ):
        self.message = message
        super().__init__(self.message)


# Helper functions
def convert_repo_url_to_api(url: str) -> str:
    """
    Converts a GitHub repository URL into the corresponding GitHub API URL to retrieve commits.

    Args:
    url (str): The GitHub repository URL.

    Returns:
    str: The corresponding GitHub API URL for commits.

    Raises:
    ValueError: If the provided URL is invalid.
    """
    # Split the URL by slashes
    parts = url.rstrip("/").split("/")

    if len(parts) < 2:
        raise ValueError("Invalid GitHub URL")

    # Extract the owner and repository name
    owner = parts[-2]
    repo = parts[-1]

    # Construct the API URL
    api_url = f"https://api.github.com/repos/{owner}/{repo}/commits"

    return api_url


# Main function
def get_github_updates(url: str) -> discord.Embed:
    """
    Retrieves the latest commits from a GitHub repository and generates an embed with the details.

    Args:
    url (str): The GitHub repository URL.

    Returns:
    discord.Embed: An embed containing the details of the latest commits.

    Raises:
    InvalidGitHubURL: If the provided URL is invalid.
    """

    # Run some checks on the URL

    # Check if the URL is empty
    if url in [None, ""]:
        raise InvalidGitHubURL("GitHub URL cannot be empty")

    # Check if the URL contains the protocol
    if not url.startswith("https://" or "http://"):
        raise InvalidGitHubURL("GitHub URL must contain the protocol (https://)")

    # Check if the URL contains the domain
    if "github.com" not in url:
        raise InvalidGitHubURL("This is not a GitHub URL")

    # Convert the repository URL to the corresponding API URL
    try:
        api_url = convert_repo_url_to_api(url)
    except ValueError:
        raise InvalidGitHubURL("Failed to convert GitHub URL to API URL")

    try:
        response = requests.get(api_url)
    except requests.exceptions.HTTPError:
        raise GithubApiError(
            "An HTTP error occurred while interacting with the GitHub API"
        )
    except requests.exceptions.ConnectionError:
        raise GithubApiError("Failed to connect to the GitHub API")
    except requests.exceptions.Timeout:
        raise GithubApiError("Connection to the GitHub API timed out")
    except requests.exceptions.TooManyRedirects:
        raise GithubApiError("Too many redirects while interacting with the GitHub API")
    except requests.exceptions.RequestException:
        raise GithubApiError("An error occurred while interacting with the GitHub API")
    except:
        raise GithubApiError(
            "An unknown error occurred while interacting with the GitHub API"
        )
    finally:
        response.raise_for_status()

    try:
        data = response.json()
    except ValueError:
        raise GithubApiError("Failed to parse the response from the GitHub API")
    except:
        raise GithubApiError("An unknown error occurred while parsing the API response")

    if not isinstance(data, list):
        raise GithubApiError("Unexpected data format received from GitHub API")

    try:
        # Sort the commits by date (newest first)
        sorted_commits = sorted(
            data,
            key=lambda x: datetime.strptime(
                x["commit"]["author"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            ),
            reverse=True,
        )
    except KeyError:
        raise GithubApiError(
            "Failed to extract commit information from the API response"
        )
    except:
        raise GithubApiError("An unknown error occurred while processing the commits")

    try:
        # Extract required information
        commit_list = []
        for commit in sorted_commits[:5]:  # Only process the latest 5 commits
            author_data = commit.get("author")
            commit_info = {
                "sha": commit["sha"],
                "id": commit["sha"][:7],
                "date": commit["commit"]["author"]["date"],
                "author": commit["commit"]["author"]["name"],
                "author_html_url": (author_data["html_url"] if author_data else "N/A"),
                "email": commit["commit"]["author"]["email"],
                "short_message": commit["commit"]["message"].split("\n")[0],
                "full_message": commit["commit"]["message"],
                "url": commit["url"],
                "html_url": commit["html_url"],
            }
            commit_list.append(commit_info)
    except KeyError:
        raise GithubApiError(
            "Failed to extract commit information from the API response"
        )
    except:
        raise GithubApiError("An unknown error occurred while processing the commits")

    # Create the embed
    desc = "Here are the latest updates to the bot:\n\n"

    for commit in commit_list:
        date = datetime.strptime(commit["date"], "%Y-%m-%dT%H:%M:%SZ")

        author_link = (
            f"[{commit['author'].split(' ')[0]}]({commit['author_html_url']})"
            if commit["author_html_url"] != "N/A"
            else commit["author"].split(" ")[0]
        )
        desc += f"**[`{commit['id']}`]({commit['html_url']})** - {format_timestamp(date, TimestampType.RELATIVE)} by {author_link}\n{commit['short_message']}\n\n"

    embed = discord.Embed(
        title="Latest Updates",
        description=desc,
        color=MAIN_EMBED_COLOR,
    )

    embed.set_footer(text="🛠️ RickBot - A project by lagden.dev")

    return embed
