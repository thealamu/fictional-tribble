import click

from api import github
from os import getenv
from os.path import isfile
from util import list_repos_from_file
from functools import partial

API_TOKEN_KEY = "GITHUB_PAT"
USERNAME_KEY = "GITHUB_USERNAME"


@click.command()
@click.option(
    "-f",
    "--file",
    "filename",
    help="File containing line-separated repository names",
)
@click.option(
    "-y", "skip_verify", is_flag=True, default=False, help="Skip delete verification"
)
def cli(filename, skip_verify):
    username, pat = getenv(USERNAME_KEY), getenv(API_TOKEN_KEY)
    github_api = github.Api(username, pat)

    # define where the repo list should come from,
    # file takes precedence over API
    repo_list_source = None
    if filename:
        if isfile(filename):
            repo_list_source = partial(list_repos_from_file, filename)
        else:
            raise Exception(f"'{filename}': No such file")
    else:
        repo_list_source = github_api.list_user_repos

    # obtain the repositories to be deleted, potentially an API call
    repositories = repo_list_source()

    if not skip_verify and repositories:
        print("\nPlease verify you want to delete these repositories:")
        if not is_verified(repositories):
            print("\nNo changes effected, your repositories are intact")
            return

    # delete the repositories
    for repo_name in repositories:
        try:
            github_api.delete_repo(repo_name)
        except Exception as e:
            print(f"Error deleting '{repo_name}': {e}")


def is_verified(repositories):
    return click.confirm(
        click.style(f"   {' '.join(repositories)}", fg="red", bold=True),
        default=False,
        show_default=True,
    )


if __name__ == "__main__":
    cli()
