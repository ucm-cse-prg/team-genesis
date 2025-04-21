# GitHub Copilot Commit Message Generation Instructions

## Overview
This document provides guidelines for generating commit messages using GitHub Copilot.

## Instructions

### 1. Write Clear and Concise Messages

 - Ensure that commit messages are clear and concise, summarizing the changes made.
 - Write commit messages in the imperative mood, as if you are giving commands. For example, use "Add feature" instead of "Added feature" or "Adding feature".
 - Keep the first line of the commit message to 50 characters or less. This helps maintain readability in various git tools and on GitHub.
 - If the commit requires more explanation, use the body of the message to provide additional context. The body should be wrapped at 72 characters.
 - If you need to include multiple points in the body, use bullet points to make it easier to read.
 - If the commit relates to a specific issue or pull request, reference it in the footer using keywords like "Fixes", "Closes", or "Resolves" followed by the issue number. This automatically links the commit to the issue on GitHub.
 - The footer can also be used to include metadata such as co-authors, breaking changes, or other relevant information.
 - If you are reverting a commit, use the format `revert: <header>` followed by the SHA of the commit being reverted in the body.

### 2. Commit Message Format

Each commit message consists of a header, a body, and a footer. The header has a special format that includes a type and a subject:

```
<type>: <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

**Example**

```
feat: Add user authentication

Added user authentication using JWT. This includes login, registration, and token verification endpoints.

- Implemented JWT-based authentication.
- Added login and registration endpoints.
- Added middleware for token verification.

Fixes #45
```

```
refactor: Update API endpoints

Refactored the API endpoints to follow RESTful conventions. 

- Updated endpoint URLs to follow RESTful conventions.
- Modified request and response formats.
```

### 3. Type must be one of the following:

 - build: Changes that affect the build system or external dependencies (example: npm packages, docker images, pypi packages, etc)
 - ci: Changes to our CI configuration files and scripts (example: GitHub Actions, Argocd)
 - docs: Documentation only changes
 - feat: A new feature or improvement to an existing feature
 - fix: A bug fix
 - perf: A code change that improves performance
 - refactor: A code change that neither fixes a bug nor adds a feature
 - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
 - test: Adding missing tests or correcting existing tests

### 4. The header is mandatory

Each type must reflect the nature of the changes made. Any line of the commit message cannot be longer 50 characters! This allows the message to be easier to read on GitHub as well as in various git tools.

### 5. The body is optional

The body should provide a more detailed explanation of the changes made in the commit. It can include information about the motivation for the change, how it was implemented, and any other relevant details.

**Example**:

```
docs: update documentation

Added new section to the documentation for the new feature.
This commit updates the documentation to include information about the new feature added in the previous commit.

- Added new section to the documentation
- Updated existing sections to reflect changes
- Fixed typos and formatting issues
- Updated links to external resources
```

```
fix: fix issue with user authentication

This commit fixes an issue with user authentication that caused errors when logging in.

closes #123
```

### 6. The footer is optional

If applicable, reference related issues and pull requests using the appropriate GitHub keywords (e.g., `Fixes #123`).

**Example**
```
fix: resolve issue with feature

This commit fixes an issue with the feature implementation.

Fixes #123
```

### 7. Revert

If the commit reverts a previous commit, it should begin with revert: , followed by the header of the reverted commit. In the body it should say: This reverts commit <hash>., where the hash is the SHA of the commit being reverted.

**Example**

```
revert: feat: add new feature
This reverts commit 1234567890abcdef1234567890abcdef12345678.
```

---

### Additional Resources
 - [GitHub Docs: Writing good commit messages](https://docs.github.com/en/github/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors)
 - [Conventional Commits Specification](https://www.conventionalcommits.org/en/v1.0.0/)


By following these guidelines, you can ensure that your commit messages are informative and helpful for anyone reviewing the project history.
