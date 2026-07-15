# splitty-cli

![Terminal first](https://img.shields.io/badge/terminal-first-00d1b2)
![ASCII powered](https://img.shields.io/badge/ASCII-powered-brightgreen)
[![PyPI version](https://img.shields.io/pypi/v/splitty-cli.svg)](https://pypi.org/project/splitty-cli/)
![Split drama](https://img.shields.io/badge/group_expense-drama_reduced-orange)
[![PyPI status](https://img.shields.io/pypi/status/splitty-cli.svg)](https://pypi.org/project/splitty-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/splitty-cli.svg)](https://pypi.org/project/splitty-cli/)
[![License](https://img.shields.io/pypi/l/splitty-cli.svg)](LICENSE)
[![Publish package to PyPI](https://github.com/0xlukem/Split-CLI/actions/workflows/publish-pypi.yml/badge.svg)](https://github.com/0xlukem/Split-CLI/actions/workflows/publish-pypi.yml)

`splitty-cli` is a Python terminal application for splitting shared expenses with a polished interactive flow, colorful terminal dashboards, and clean settlement suggestions.

## Features

- guided step-by-step CLI powered by Typer
- styled prompts, tables, panels, and dashboards with Rich
- animated intro and terminal charts, with a no-animation mode for simpler sessions
- equal split calculations with cent-accurate rounding
- minimized settlement transfers between debtors and creditors
- expense analytics with terminal charts
- optional JSON export for every completed session
- modular business logic with Pydantic validation and pytest coverage

## Installation

```bash
pip install splitty-cli
```

## Quickstart

Run the interactive app:

```bash
splitty-cli
```

Disable the animated intro when you want a quieter run, a simpler terminal capture, or better compatibility with a limited terminal:

```bash
splitty-cli --no-animations
```

You can also disable animations with an environment variable:

```bash
SPLITTY_NO_ANIMATIONS=1 splitty-cli
```

Follow the prompts to:

1. name the event
2. add the participants
3. enter each expense
4. review balances, settlements, and charts
5. optionally export the session to JSON

## JSON export

Write the final report to a JSON file:

```bash
splitty-cli --export-json reports/weekend-trip.json
```

In the interactive flow, JSON backups are stored by default in `~/.splitty-cli/backups/` and use the pattern `<event-name>-YYYY-MM-DD.json`.
If you confirm the export at the end of the session, the CLI only asks for the backup file name and keeps the file inside that folder.

The exported report includes:

- event summary
- participant balances
- settlement transfers
- analytics insights
- expense and payer breakdown data

