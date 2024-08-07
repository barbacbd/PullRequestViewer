# Pull Request Viewer

The project was created as a simple script to assist with viewing what pull requests were still open for members of a team.

The user can edit the example configuration file to supply:
- Github Access Token
- Projects/Repositories
- PR Authors
- Labels (optional)
- JIRA Access Token (optional)
- JIRA url (optional)
- JIRA Board ID (optional)

The script will search for open pull requests in each project and user/author combination supplied in the configuration file. The output will contain the author, PR Title, PR number, PR link, and whether or not the labels were present (for each provided).

## Access Token 

The github access token can be generated by visiting

```
Settings -> Developer Settings -> Personal Access Tokens
```

The access token should have read access to all fields, but no write access is required.

### Notes
- The access token cannot be seen forever, so copy it some where safe and accessible
- When creating the access token there is a time limit to the tokens availability

## Repositories

The `repos` value in the configuration file **must** include the `owner` and `name`. For instance if you would like to select a repository from
`github.com/example-user/test-repo` the following must be in the configuration file:

```yaml
repos:
  - owner: example-user
    name: test-repo
```

This is a list, so the user may enter as many repositories as they wish. Each repository where pull requests were found will be added as a sheet to the output spreadsheet.

## Authors

The `users` value in the configuration file is the list of authors that have opened pull requests. If there is an open pull request from a user in the list, it will be added to the final spreadsheet.

```yaml
users:
  - example-user-1
  - example-user-2
```

This is a list, so each author/user entered here will used during the search.

## Labels

The `labels` tag is optional. When labels contains data, each label will be searched in the list of labels attached to each pull request. The final spreadsheet will provide a true/false value of whether or not the label was present on the pull request.

```yaml
labels:
  - approve
```

The example above will search the pull request for the label `approve`. If approve is present on the pull request the spreadsheet will indicate true for present.

# JIRA

The user must supply all JIRA contents for this section to be valid.

## JIRA Access Token

The JIRA access token can be generated by visiting

```
Profile -> Personal Access Tokens -> Create Token
```

### Notes
- The access token cannot be seen forever, so copy it some where safe and accessible
- When creating the access token there is a time limit to the tokens availability

## JIRA Url

The base url for the JIRA website where the data should be pulled.

## JIRA Board ID

The Board is where all JIRA cards will be set. The following is an example:

```
https:/example.jira.com/RapidBoard.jspa?rapidView=1234
```

In the above example, `1234` is the ID of the Board. 