# Plimsoll

Parametric naval-architecture calculation: a Python calculation core with a command-line interface, and a web
workspace built on top of it (React front end, FastAPI service).

**Licence: MIT** (`LICENSE`, copyright 2026 Yang Rui). Third-party components and bundled assets are listed in
`THIRD-PARTY.md`.

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

## Install and run

The **core needs Python 3.12+ and nothing else** — it imports only the standard library:

```bash
python tools/plimsoll/cli.py --help
python tools/plimsoll/cli.py tools/plimsoll/cases/generic_test_steamer_1910.json
```

Installable form, which also puts a `plimsoll` command on your path:

```bash
pip install -e .          # from the repository root
plimsoll --help
```

The core regression:

```bash
python tools/plimsoll/run_all_tests.py     # prints PLIMSOLL_REGRESSION run=<n> fail=<n>
```

**Known and pre-existing:** four of those tests fail wherever the package is not importable as `tools.plimsoll.*`
(`test_damage_lab`, `test_damage_lab_cli`, `test_damage_lab_vessel`, `test_fragmentation`). They fail identically
in the author's private repository, so that baseline is the reference, not zero.

The web workspace needs Node.js and a Python environment with the backend's dependencies:

```bash
cd web/frontend && npm ci && npm run dev         # http://127.0.0.1:5173
cd web/backend  && pip install -e '.[dev]' && alembic upgrade head
cd web/backend  && pytest                        # the service's own suite
```

Vite must keep port 5173 in development: the service's allowed origin is pinned to it. `web/deploy/` documents
the production shape (PostgreSQL, nginx, container).

## What is not here, on purpose

Historical-ship case data (the Queen Mary case and the tests anchored on it), the game/3D modelling material and
the project's internal development records stay in the author's private repository. This repository carries the
**general** tool with synthetic study cases.

## Honest limits

The core documents its own uncertainty instead of hiding it: `method_versions`, per-value `source` and `estimate`
flags, `historical_validation` and explicit unknowns are part of the data model, and several quantities are
deliberately left unknown rather than guessed. Results are engineering estimates — not surveyed, class-approved
or experimentally validated values — and the interface says so where it matters.

## Contributing

See `CONTRIBUTING.md`. Contributions are accepted under the MIT licence.
