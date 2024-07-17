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
import inquirer
from yaml import dump


def ask_for_github_token():
    """Ask the user for their github access token.

    To create a github access token visit:
    github -> settings -> developer settings -> personal access tokens.
    
    :return: A Dictionary where the main key is "github_access_token".
    """
    questions = [inquirer.Password("access_token", message="Github access token")]
    answers = inquirer.prompt(questions)
    return {"github_access_token": answers["access_token"]}


def ask_for_users():
    """Ask the user to enter the github users.
    
    :return: A dictionary where the main key is "users".
    """
    continue_asking = True

    users = set()
    while continue_asking:
        questions = [
            inquirer.Text("user", message="Github username"),
            inquirer.List("continue_asking", message="Enter more users?", choices=["yes", "no"]), 
        ]

        answers = inquirer.prompt(questions)

        user = answers["user"]
        if not user:
            break

        users.add(user)
        continue_asking = answers["continue_asking"] == "yes"

    return {"users": list(users)}


def ask_for_labels():
    """Ask the user to enter the github labels.
    
    :return: A dictionary where the main key is "labels".
    """
    continue_asking = True

    labels = set()
    while continue_asking:
        questions = [
            inquirer.Text("label", message="Label"),
            inquirer.List("continue_asking", message="Enter more labels?", choices=["yes", "no"]), 
        ]

        answers = inquirer.prompt(questions)

        label = answers["label"]
        if not label:
            break

        labels.add(label)
        continue_asking = answers["continue_asking"] == "yes"

    return {"labels": list(labels)}


def ask_for_repos():
    """Ask the user to enter the github repos.
    Each repo contains a repo name and owner.

    :return: A dictionary where the main key is "repos".
    """
    continue_asking = True

    repos = []
    while continue_asking:
        questions = [
            inquirer.Text("owner", message="repo owner"),
            inquirer.Text("name", message="repo name"),
            inquirer.List("continue_asking", message="Enter more repos?", choices=["yes", "no"]), 
        ]

        answers = inquirer.prompt(questions)

        owner = answers["owner"]
        if not owner:
            break
    
        name = answers["name"]
        if not name:
            break

        repos.append({"owner": owner, "name": name})
        continue_asking = answers["continue_asking"] == "yes"

    return {"repos": repos}


def ask_for_jira_token():
    """Ask the user for their jira access token.

    To create a jira access token visit:
    profile -> personal access tokens -> create token

    :return: A Dictionary where the main key is "jira_access_token".
    """
    questions = [inquirer.Password("access_token", message="JIRA access token")]
    answers = inquirer.prompt(questions)
    return {"jira_access_token": answers["access_token"]}


def ask_for_jira_url():
    """Ask the user for their jira base url.

    :return: A Dictionary where the main key is "jira url".
    """
    questions = [inquirer.Password("url", message="JIRA url")]
    answers = inquirer.prompt(questions)
    return {"jira_url": answers["url"]}


def ask_for_jira_board_id():
    """Ask the user for a jira board id. 

    :return: A dictionary where the main key is "board_id".
    """
    questions = [inquirer.Password("board_id", message="JIRA Board ID")]
    answers = inquirer.prompt(questions)
    return {"board_id": answers["board_id"]}


def create_config(filename, coordinate_with_jira=False):
    """Create a configuration for a yaml config file.

    :param filename: name of the configuration file that will be created.
    :param coordinate_with_jira: When true ask for jira access information.
    """
    call_functions = [ask_for_github_token, ask_for_users, ask_for_labels, ask_for_repos]
    if coordinate_with_jira:
        call_functions.extend([ask_for_jira_token, ask_for_jira_url, ask_for_jira_board_id])

    config = {}
    for call_func in call_functions:
        config.update(call_func())
    
    with open(filename, "w") as config_file:
        config_file.write(dump(config, indent=2))
