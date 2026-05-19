# .github Configuration
![Python Lint](https://github.com/Ambibuzz/.github/actions/workflows/pylint.yml/badge.svg)
![JS Lint](https://github.com/Ambibuzz/.github/actions/workflows/jslint.yml/badge.svg)
![Review Workflow](https://github.com/Ambibuzz/.github/actions/workflows/review.yml/badge.svg)
![Pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)
![Conventional Commits](https://img.shields.io/badge/commits-conventional-blue?logo=git&logoColor=white)

This repository serves as the central configuration and health repository for **Ambibuzz Technologies LLP**. It mirrors the special `.github` repository pattern supported by GitHub to provide default community health files and configurations for the organization.
## Table of Contents

- [Purpose](#purpose)
- [Tools & Configurations](#tools--configurations)
  - [Python Linting & Formatting (`ruff.toml`)](#1-python-linting--formatting-rufftoml)
  - [Commit Message Linting (`commitlint.config.js`)](#2-commit-message-linting-commitlintconfigjs)
  - [Pre-commit Hooks (`.pre-commit-config.yaml`)](#3-pre-commit-hooks-pre-commit-configyaml)
- [Workflows (GitHub Actions)](#workflows-github-actions)
- [Setup Instructions](#setup-instructions)
- [Repository Structure](#repository-structure)
- [Contact](#contact)
## Purpose

The primary purpose of this repository is to store reusable configurations and workflows that can be inherited or referenced by other repositories within the organization. This ensures consistency in coding standards, commit messages, and CI/CD processes.

## Tools & Configurations

The following tools and configurations are maintained in this repository:

### 1. Python Linting & Formatting (`ruff.toml`)

We use **Ruff** for extremely fast Python linting and formatting.

- **Config File**: [`ruff.toml`](ruff.toml)
- **Settings**:
  - Target Python Version: 3.10
  - Line Length: 110
  - Indent Style: Tab
  - Rules: Flake8 (F), pycodestyle (E, W), isort (I), pyupgrade (UP), bugbear (B), and Ruff specific rules (RUF).

### 2. Commit Message Linting (`commitlint.config.js`)

We enforce **Conventional Commits** to ensure a clean and structured commit history.

- **Config File**: [`commitlint.config.js`](commitlint.config.js)
- **Standard**: Conventional Commits (via `@commitlint/config-conventional`)

### 3. Pre-commit Hooks (`.pre-commit-config.yaml`)

A set of Git hooks to automatically identify and fix issues before code is committed.

- **Config File**: [`.pre-commit-config.yaml`](.pre-commit-config.yaml)
- **Hooks**:
  - `trailing-whitespace`
  - `end-of-file-fixer`
  - `check-yaml`, `check-json`, `check-toml`
  - `ruff-check` & `ruff-format` (Python)
  - `prettier` (JS, CSS, SCSS, etc.)
  - `commitlint` (Commit messages)

## Setup

To ensure code quality and consistency, please set up the Git hooks locally:

1. **Install `pre-commit`**:

   ```bash
   pip install pre-commit
   ```

2. **Install the hooks**:
   ```bash
   pre-commit install
   pre-commit install --hook-type commit-msg
   ```

## Workflows

GitHub Actions workflows are located in `.github/workflows/` and can be used for checking code quality across repositories.

- **`pylint.yml`**: Runs Pylint checks.
- **`jslint.yml`**: Runs JavaScript linting.
- **`review.yml`**: General review workflow.

## Templates

- **Pull Request Template**: Located at `.github/PULL_REQUEST_TEMPLATE.md`, this template is automatically applied to new Pull Requests in the organization to guide contributors in providing necessary context.

- **Repository Structure**:A quick overview of the key files and folders:
```
├── .github/
│   ├── workflows/
│   │   ├── pylint.yml
│   │   ├── jslint.yml
│   │   └── review.yml
│   └── PULL_REQUEST_TEMPLATE.md
├── .pre-commit-config.yaml
├── commitlint.config.js
├── ruff.toml
└── README.md
```

## license

MIT

## Maintainers

This application is actively maintained by **Ambibuzz Technologies LLP**. For any issues, please raise a GitHub issue or contact us.

## Contact

- GitHub: [Ambibuzz](https://github.com/Ambibuzz)
- Website: [ambibuzz.com](https://www.ambibuzz.com)
- Email: [buzz.us@ambibuzz.com](mailto:buzz.us@ambibuzz.com)
