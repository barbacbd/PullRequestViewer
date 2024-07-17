"""
MIT License

Copyright (c) 2024 Brent Barbachem

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from os.path import exists
from collections import OrderedDict
from atlassian import Jira
from github import Github
from github.GithubException import BadCredentialsException
from yaml import safe_load
import pandas as pd


def _read_config(config_filename):
    """Read in the config filename data.

    :return: YAML config data as a dictionary.
    """
    if not exists(config_filename):
        print(f"failed to find {config_filename}")
        return

    # pylint: disable=unspecified-encoding
    with open(config_filename, "r") as yaml_file:
        data = safe_load(yaml_file.read())

        for key in ["github_access_token", "users", "repos"]:
            if key not in data:
                print(f"failed to find {key} in configuration file {config_filename}")
                return
    return data


def access_github_info(access_token, users, repos, search_labels=[]):
    """Parse the github information from the configuration file.

    The following is a dictionary that will contain a list of tuples with
    the format:
    ( user, pull request title, pull request number, pull request url, ... (labels) )
    Each tuple will be placed into the dictionary with the key for the repo.
    The data will be stored as a sheet in an excel file that is generated
    at the conclusion of this script.
    """
    github_obj = Github(access_token)

    github_output = {}

    for repo_info in repos:

        if "owner" not in repo_info or "name" not in repo_info:
            print(f"repos must contain owner and name, skipping {repo_info}")
            continue

        repo_owner = repo_info["owner"]
        repo_name = repo_info["name"]
        labeled_name = f"{repo_owner}.{repo_name}"
        try:
            repo = github_obj.get_repo(f"{repo_owner}/{repo_name}")
        except BadCredentialsException:
            print("Insufficient permissions, please check the access token.")
            print("To create an access token, visit: ")
            print("github -> settings -> developer settings -> personal access tokens")
            return

        github_output[labeled_name] = []

        for pull_request in repo.get_pulls(state='open'):
            if pull_request.user.login in users:

                labels = [label.name for label in pull_request.labels]
                labels_values = [label in labels
                    for label in search_labels
                ]

                github_output[labeled_name].append(
                    [
                        pull_request.user.login,
                        pull_request.title,
                        pull_request.number,
                        pull_request.html_url,
                    ] + labels_values
                )

    return github_output


def find_jira_issues(jira_access_token, jira_url, jira_board_id):
    """Find all issues in the current sprint.
    
    :param jira_access_token: To create a jira access token visit:
        profile -> personal access tokens -> create token.
    :param jira_url: The base url for JIRA.
    :param jira_board_id: The id of the jira board.
    """
    jira = Jira(url=jira_url, token=jira_access_token)

    try:
        _board_id = int(jira_board_id)
    except TypeError:
        print("failed to convert board id to integer")
        return
    
    # get the active sprints in the board supplied by the user
    jira_sprints = jira.get_all_sprints_from_board(_board_id, state="active")
    
    # find the only sprint listed that matches
    sprint_data = [x for x in jira_sprints["values"] if x["originBoardId"] == _board_id]
    if len(sprint_data) < 1:
        print("failed to find current sprint data")
        return
    
    sprint_data = sprint_data[0]

    if "id"	not in sprint_data:
        print("failed to find sprint id")
        return

    # Set the limit large for now, but this could be configured or 
    # autmatically adjusted later
    issues = jira.get_all_issues_for_sprint_in_board(_board_id, sprint_data["id"], limit=200)

    if "issues" not	in issues:
        print("failed to find sprint issues")
        return

    return [issue["key"] for issue in issues["issues"]]


def coordinate_jira_data(github_data, jira_issues):
    """Coordinate JIRA and Github information. This will find the github pull
    reuqests that are open for current JIRA tickets in the open/active sprint.

    :param github_data: A list of lists, 
        ( user, pull request title, pull request number, pull request url, ... (labels) )
    :param jira_issues: list of jira issue names

    The following is a dictionary that will contain a list of tuples with
    the format:
    ( user, pull request title, pull request number, pull request url, ... (labels) )
    Each tuple will be placed into the dictionary with the key for the repo.
    The data will be stored as a sheet in an excel file that is generated
    at the conclusion of this script.
    """
    output = []
    for issue in jira_issues:
        for _, github_prs in github_data.items():
            # do not skip on check if one is found, sometimes
            # there are multiple cards for a single jira issue.
            for github_pr in github_prs:
                if issue.lower() in github_pr[1].lower():
                    output.append(github_pr)
    
    return output


def build_report(config_filename, output_filename):
    """Build the excel report

    :param config_filename: Name of the configuration (input) file where the yaml 
    data will be loaded from.
    :param output_filename: Excel file where the data will be output.
    """
    config_data = _read_config(config_filename)
    if config_data is None:
        return

    # Parse the config.yaml file. If the file does not exist then the
    # program will not execute.
    access_token = config_data["github_access_token"]  # pylint: disable=invalid-name
    users = config_data["users"]
    repos = config_data["repos"]

    # These are optional args
    search_labels = config_data["labels"] if "labels" in config_data else []
    
    jira_access_token = None  # pylint: disable=invalid-name
    if "jira_access_token" in config_data:
        jira_access_token = config_data["jira_access_token"]

    jira_url = None  # pylint: disable=invalid-name
    if "jira_url" in config_data:
        jira_url = config_data["jira_url"]

    jira_board_id = None  # pylint: disable=invalid-name
    if "board_id" in config_data:
        jira_board_id = config_data["board_id"]

    github_output = access_github_info(access_token, users, repos, search_labels=search_labels)
    github_output = OrderedDict(github_output)

    if None not in (jira_access_token, jira_url, jira_board_id):
        jira_issues = find_jira_issues(jira_access_token, jira_url, jira_board_id)
        jira_github_coordinated_output = coordinate_jira_data(github_output, jira_issues)
        github_output["jira"] = jira_github_coordinated_output
        github_output.move_to_end("jira", last=False)

    columns = [
        "Author",
        "Title",
        "PR Number",
        "Link",
    ] + search_labels

    # clear out the empty results from the final output
    # convert the value to a dataframe for each value in the dictionary
    github_output = {
        key: pd.DataFrame(value, columns=columns)
        for key, value in github_output.items()
        if value != []
    }

    # pylint: disable=abstract-class-instantiated
    writer = pd.ExcelWriter(output_filename, engine='xlsxwriter')
    # output the data to an excel file.
    # auto scale the size of the column as well for easier viewing.
    for sheetname, df in github_output.items():
        df.to_excel(writer, sheet_name=sheetname, index=False)
        worksheet = writer.sheets[sheetname]
        for idx, col in enumerate(df):
            series = df[col]
            max_len = max((
                series.astype(str).map(len).max(),
                len(str(series.name))
            )) + 1
            worksheet.set_column(idx, idx, max_len)
    writer.close()
