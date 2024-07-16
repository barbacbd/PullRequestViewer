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


def ask_for_token():
    """Ask the user for their github access token.
    
    :return: A Dictionary where the main key is "access_token".
    """
    questions = [inquirer.Password("access_token", message="Github access token")]
    answers = inquirer.prompt(questions)
    return {"access_token": answers["access_token"]}


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


def create_config(filename):
    """Create a configuration for a yaml config file.

    :param filename: name of the configuration file that will be created.
    """
    config = {}
    for call_func in [
        ask_for_token, 
        ask_for_users, 
        ask_for_labels, 
        ask_for_repos
    ]:
        config.update(call_func())
    
    with open(filename, "w") as config_file:
        config_file.write(dump(config, indent=2))
