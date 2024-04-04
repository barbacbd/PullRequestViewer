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
import argparse
from os.path import exists
import sys
from github import Github
from yaml import safe_load
import pandas as pd


parser = argparse.ArgumentParser()
parser.add_argument(
    "--input",
    dest="input_file",
    default="config.yaml",
    help="configuration yaml file"
)
parser.add_argument(
    "--output",
    dest="output_file",
    default="github.xlsx",
    help="output excel file"
)
args = parser.parse_args()

_filename = args.input_file
_output_file = args.output_file

if not exists(_filename):
    print(f"failed to find {_filename}")
    sys.exit(1)

# Parse the config.yaml file. If the file does not exist then the
# program will not execute.
access_token = None  # pylint: disable=invalid-name
users = []
repos = []
search_labels = []

# pylint: disable=unspecified-encoding
with open(_filename, "r") as yaml_file:
    data = safe_load(yaml_file.read())

    for key in ["access_token", "users", "repos"]:
        if key not in data:
            print(f"failed to find {key} in configuration file {_filename}")
            sys.exit(2)

    access_token = data["access_token"]
    users = data["users"]
    repos = data["repos"]

    # optional parameters
    if "labels" in data:
        search_labels = data["labels"]

github_obj = Github(access_token)

# The following is a dictionary that will contain a list of tuples with
# the following format:
# ( user, pull request number, pull request url, pull request title, ... (labels) )
# Each tuple will be placed into the dictionary with the key for the repo.
# The data will be stored as a sheet in an excel file that is generated
# at the conclusion of this script.
github_output = {}

for repo_info in repos:

    if "owner" not in repo_info or "name" not in repo_info:
        print(f"repos must contain owner and name, skipping {repo_info}")
        continue

    repo_owner = repo_info["owner"]
    repo_name = repo_info["name"]
    labeled_name = f"{repo_owner}.{repo_name}"
    repo = github_obj.get_repo(f"{repo_owner}/{repo_name}")
    github_output[labeled_name] = []

    for pull_request in repo.get_pulls(state='open'):
        if pull_request.user.login in users:

            labels = [label.name for label in pull_request.labels]
            labels_values = [label in labels
                for label in search_labels
            ]

            lgtmd = "lgtm" in labels
            approved = "approved" in labels

            github_output[labeled_name].append(
                [
                    pull_request.user.login,
                    pull_request.title,
                    pull_request.number,
                    pull_request.html_url,
                ] + labels_values
            )


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
writer = pd.ExcelWriter(_output_file, engine='xlsxwriter')
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
