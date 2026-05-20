# GitHub Usage Rules

## 1. Repository Structure and Branching Strategy
We are using a monorepo structure for our project with a GitFlow branching stratergy. 
The main branches are:
- `main`: This branch contains the stable code that is ready for production. All releases are made from this branch. (This branch is protected and requires pull requests for any changes.)
- `dev`: This branch is used for ongoing development.

</br>

Feature branches are created from `dev` and are used for developing new features or fixing bugs. Individuals are to create their own branches from these feature branches for their specific tasks. The naming convention for feature branches is as follows: `featureName_yourName`.
- `frontend`
- `user`
- `guest`
- `admin`
- `firefighter`

</br>

# 2. Project Board
The project board consists of the following columns:
- `Backlog`: This column contains all the tasks that need to be done but have not yet been started.
- `Ready`: This column contains tasks that are ready to be worked on. These tasks have been prioritized and assigned to team members.
- `In Progress`: This column contains tasks that are currently being worked on.
- `Review`: This column contains tasks that have been completed and are awaiting review. In terms of code tasks, the issue may only be moved into this column once a pull request has been created and is ready for review.
- `Done`: This column contains tasks that have been reviewed and approved.

</br>

Side note: If you create an issue and create subissues for it, please keep the main issue (the one with a purple bar on it) in the `Backlog` column until all the subissues are completed. Once all the subissues are completed, you can move the main issue to the `Done` column. This helps us keep track of the progress of larger tasks that may have multiple components.

</br>

# 3. Pull Request Guidelines
When creating a pull request, please follow these guidelines:
- Ensure that your code is well-documented and follows the coding standards of the project.
- Provide a clear and concise description of the changes you have made.
- Please ensure you add Megan as a reviewer to your pull request for code review and approval.
