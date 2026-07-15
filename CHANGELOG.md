# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

No unreleased changes yet.

## [0.1.0b1] - 2026-07-15

### Added

- Added an animated Splitty intro with compact fallback for CI, non-terminal output, and small terminals.
- Added `--animations/--no-animations` to control the animated intro.
- Added animated chart rendering for expense and payer breakdowns.
- Added compact highlight badges for top spender and most expensive expense insights.
- Added test coverage for intro rendering, animation fallback, chart animation, and the no-animation CLI flow.

### Changed

- Promoted the package metadata from alpha to beta.
- Replaced the previous static welcome banner with the new Splitty intro.
- Improved chart rendering stability by keeping the x-axis fixed during animation.
- Updated the project homepage metadata to the active GitHub repository.

### Fixed

- Fixed the terminal tagline copy in the intro.
- Removed trailing whitespace from the compact intro art.

### Known limitations

- Equal split only across all participants.
- No CSV export yet.
- Richer visual exports are not available yet.
