# Plimsoll

**Parametric naval-architecture calculations you can audit.** Plimsoll computes hydrostatics, stability, loading,
flooding and damage for a parametric vessel, and it records *where every number came from*: a method version per
kernel, a `source` and `estimate` flag per value, and explicit unknowns where an input is missing.

It is a Python calculation core with a command-line interface, and a bilingual (English / 中文) web workspace built
on it — project revisions, calculation runs, a readable report with switchable display units and JSON/CSV export,
and a damage laboratory for hit studies.

**Licence: MIT** (`LICENSE`, copyright 2026 Yang Rui). Third-party components and bundled assets are listed in
`THIRD-PARTY.md`.

## Why it exists

Most engineering calculators give you a number and hide the reasoning. Plimsoll is built the other way round:

- **Unknowns stay unknown.** A quantity nobody supplied is `null`, never a plausible-looking default, and it is
  never silently turned into a zero.
- **Every value carries its provenance.** Kernels are versioned (`connected-quasi-static-flooding-3`,
  `holtrop_mennen_1982`, …) and data carries `source` / `estimate` markers, so an engineering proxy is never
  mistaken for a measured or historically validated value.
- **Comparisons refuse to lie.** Two runs are differenced only when they share their basis (revision, condition,
  method versions). Every compared cell is `known`, `unknown`, `unrequested` or `incompatible`; the direction is
  always stated (comparison minus current); an unknown operand yields an unknown difference, not a zero.
- **Explanations are derived from records, not prose.** The laboratory explains a damaged target from its recorded
  fragment paths, boundary responses and accepted events. It never parses a log message, and a frame accepted
  before the detonation reveals nothing that happened later.
- **Verification ships with the code.** Independent oracles, convergence studies and recorded core-verification
  reports are part of the repository.

## Quick start

The core needs **Python 3.12+ and no third-party packages**:

```bash
python tools/plimsoll/cli.py --help
python tools/plimsoll/cli.py tools/plimsoll/cases/generic_test_steamer_1910.json
python tools/plimsoll/run_all_tests.py        # the core regression
```

Installable form, which also puts a `plimsoll` command on your path:

```bash
pip install -e .          # from the repository root
plimsoll --help
```

The web workspace needs Node.js and a Python environment:

```bash
pip install -e .                                  # the core first: the service imports it
cd web/frontend && npm ci && npm run dev          # http://127.0.0.1:5173
cd web/backend  && pip install -e '.[dev]' && alembic upgrade head
cd web/backend  && pytest
```

Vite must keep port 5173 in development: the service's allowed origin is pinned to it. `web/deploy/` documents the
production shape (PostgreSQL, nginx, container).

## Layout

| path | what it is |
|---|---|
| `tools/plimsoll/` | the calculation core and the CLI, with its test suite and synthetic cases |
| `web/frontend/` | the React workspace, damage laboratory and public shell (Vite + TypeScript) |
| `web/backend/` | the FastAPI service: projects, revisions, runs, the worker |
| `web/deploy/` | container, nginx template and release-building material |
| `web/dev/` | an anonymous-mode local service for offline work |
| `docs/plimsoll-1.0/` | specification, current status and engineering evidence |
| `data/` | the armour-standards dataset the core reads |

## Status

Alpha, and honest about it. The core regression runs **592 tests**; four of them fail in any environment where the
package is not importable as `tools.plimsoll.*` — a known, pre-existing property of the test runner, present in the
author's private repository too, not a regression. The web suites are green: **792 front-end tests**, and **109
service tests with 4 skipped** because they exercise a large inline-geometry fixture this repository does not carry.

**These are engineering estimates.** Nothing here is class-approved, surveyed or experimentally validated, and the
interface says so wherever it matters.

## What this repository does not contain

Historical-ship case data (and the tests anchored on it), the game/3D modelling material, and the project's internal
development records stay in the author's private repository. This is the general tool, with synthetic study cases.

## Licence and third-party components

MIT — see `LICENSE`. Bundled fonts are SIL OFL 1.1 and ship their licence texts; the interaction sounds are original
works of this project; dependency licences are listed in `THIRD-PARTY.md`, including the one non-permissive
dependency (**psycopg, LGPL-3.0-only**, used as an installed library rather than linked into Plimsoll's own source).

Some calculation data was transcribed by the author from university textbooks, and the files say which. For example
`tools/plimsoll/cases/taylor_gertler_cr_table.json` records *Molland, Turnock & Hudson, Ship Resistance and
Propulsion*, Appendix A3, Tables A3.8 to A3.11 (pp. 495-498).

## Contributing

See `CONTRIBUTING.md`. Contributions are accepted under the MIT licence. The rules that matter most: numbers stay
honest (an unknown stays unknown), user-facing strings are added in both languages, and a claim that can be measured
is measured.

[中文说明](README.zh-CN.md)
