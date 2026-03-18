# split-cli

`split-cli` is a Python terminal application for splitting shared expenses with a polished interactive flow, colorful terminal dashboards, and clean settlement suggestions.

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
pip install --pre split-cli
```

## Quickstart

Run the interactive app:

```bash
split-cli
```

Or run it directly from the source tree:

```bash
PYTHONPATH=src python -m split_cli.cli
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
split-cli --export-json reports/weekend-trip.json
```

The exported report includes:

- event summary
- participant balances
- settlement transfers
- analytics insights
- expense and payer breakdown data

## Current limitations

- equal split only across all participants
- no weighted shares or per-person consumption
- no saved history yet
- no CSV export yet
- better grap
- UI animations