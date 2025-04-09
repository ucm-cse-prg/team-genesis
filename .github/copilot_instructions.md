# GitHub Copilot Commit Message Generation Instructions

## Overview
This document provides guidelines for generating commit messages using GitHub Copilot.

## Instructions

1. **Write Clear and Concise Messages**: Ensure that commit messages are clear and concise, summarizing the changes made.

3. **Commit Message Format**: Each commit message consists of a header, a body, and a footer. The header has a special format that includes a type and a subject:
    ```
    <type>: <subject>
    <BLANK LINE>
    <body>
    <BLANK LINE>
    <footer>
    ```

4. **The header is mandatory**: Each type must reflect the nature of the changes made. Any line of the commit message cannot be longer 50 characters! This allows the message to be easier to read on GitHub as well as in various git tools.

The footer should contain a closing reference to an issue if any.

Samples: (even more samples)

docs(changelog): update changelog to beta.5

fix(release): need to depend on latest rxjs and zone.js



5. **Revert**:

If the commit reverts a previous commit, it should begin with revert: , followed by the header of the reverted commit. In the body it should say: This reverts commit <hash>., where the hash is the SHA of the commit being reverted.

6. **Type**: Type must be one of the following:

 - build: Changes that affect the build system or external dependencies (example scopes: gulp, broccoli, npm)
 - ci: Changes to our CI configuration files and scripts (example scopes: Travis, Circle, BrowserStack, SauceLabs)
 - docs: Documentation only changes
 - feat: A new feature
 - fix: A bug fix
 - perf: A code change that improves performance
 - refactor: A code change that neither fixes a bug nor adds a feature
 - style: Changes that do not affect the meaning of the code (white-space, formatting, missing semi-colons, etc)
 - test: Adding missing tests or correcting existing tests

4. **Reference Issues and PRs**: If applicable, reference related issues and pull requests using the appropriate GitHub keywords (e.g., `Fixes #123`).


## Example
```
feat: add new feature

This commit adds a new feature to the project.
```

```
fix: resolve issue with feature

This commit fixes an issue with the feature implementation.

Fixes #123
```

## Additional Resources
- [GitHub Docs: Writing good commit messages](https://docs.github.com/en/github/committing-changes-to-your-project/creating-and-editing-commits/creating-a-commit-with-multiple-authors)

By following these guidelines, you can ensure that your commit messages are informative and helpful for anyone reviewing the project history.
