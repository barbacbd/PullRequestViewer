# Pull Request Viewer

The project was created as a simple script to assist with viewing what pull requests were still open for members of a team.

The user can edit the example configuration file to supply:
- Github Access Token
- Projects/Repositories
- PR Authors
- Labels (optional)

The script will search for open pull requests in each project and user/author combination supplied in the configuration file. The output will contain the author, PR Title, PR number, PR link, and whether or not the labels were present (for each provided).
