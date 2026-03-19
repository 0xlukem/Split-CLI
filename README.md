# splitty-cli

`splitty-cli` is a Python terminal application for splitting shared expenses with a polished interactive flow, colorful terminal dashboards, and clean settlement suggestions.

## Features

- guided step-by-step CLI powered by Typer
- styled prompts, tables, panels, and dashboards with Rich
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

## Current limitations

- equal split only across all participants
- no CSV export yet
- better graphics
- UI animations
