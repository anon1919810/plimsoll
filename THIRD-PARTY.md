# Third-party notices

Plimsoll itself is MIT-licensed (see `LICENSE`). This file records what the repository bundles or depends on,
and under what terms. The licences below were read from the **installed package metadata** of the versions in
this repository's lockfile and virtualenv, not from memory.

Scope: **direct dependencies and bundled assets.** This is not a transitive software bill of materials; if you
need one, `npm ls --all` in `web/frontend` and `pip freeze` in the backend virtualenv enumerate it.

---

## Fonts (bundled, self-hosted)

All four families are under the **SIL Open Font License 1.1**, which permits bundling with an application.
The full licence text for each ships beside the font files in `web/frontend/public/fonts/`, together with
SHA-256 checksums and the official source URLs (`web/frontend/public/fonts/README.md`).

| family | licence text | copyright |
|---|---|---|
| Archivo | `Archivo-OFL.txt` | Copyright 2020 The Archivo Project Authors (Omnibus-Type) |
| Inter | `Inter-OFL.txt` | Copyright (c) 2016 The Inter Project Authors |
| Space Grotesk | `SpaceGrotesk-OFL.txt` | Copyright 2020 The Space Grotesk Project Authors |
| Caveat | `Caveat-OFL.txt` | Copyright 2016 The Caveat Project Authors |

The reserved-font-name rule is respected: no family is renamed, and no font file is sold on its own.

## Interaction sounds (bundled)

`web/frontend/public/audio/*.wav` are **original works of this project**, synthesised deterministically with the
Python standard library from `tools/render_formfield_sounds.py`. No external samples are used. The provenance,
durations and SHA-256 checksums are in `web/frontend/public/audio/README.md`.

## Artwork (bundled)

`web/frontend/public/portfolio/` holds reference line sheets **supplied by the project author** and lossless WebP
derivatives of them, plus one screenshot of a Plimsoll report produced by the author. Provenance, dimensions and
checksums are in `web/frontend/public/portfolio/PROVENANCE.md`.

## JavaScript dependencies (installed, not vendored)

| package | version | licence |
|---|---|---|
| react | 19.3.0 | MIT |
| react-dom | 19.3.0 | MIT |
| three | 0.186.1 | MIT |
| @testing-library/jest-dom | 7.0.1 | MIT |
| @testing-library/react | 16.3.3 | MIT |
| @types/react | 19.3.0 | MIT |
| @types/react-dom | 19.3.0 | MIT |
| @types/three | 0.186.0 | MIT |
| @vitejs/plugin-react | 6.1.1 | MIT |
| jsdom | 30.1.1 | MIT |
| typescript | 7.0.2 | Apache-2.0 |
| vite | 8.3.0 | MIT |
| vitest | 5.0.1 | MIT |

## Python dependencies (installed, not vendored)

| package | version | licence |
|---|---|---|
| fastapi | 0.141.1 | MIT |
| starlette | 1.7.0 | BSD-3-Clause |
| pydantic | 2.13.5 | MIT |
| SQLAlchemy | 2.0.54 | MIT |
| alembic | 1.20.0 | MIT |
| uvicorn | 0.53.0 | BSD-3-Clause |
| email-validator | 2.3.0 | Unlicense |
| httpx | 0.28.1 | BSD-3-Clause |
| pytest | 9.1.1 | MIT |
| **psycopg** | 3.3.6 | **LGPL-3.0-only** |

**Note on psycopg.** It is the one dependency here that is not permissive: LGPL-3.0-only. It is used as an
installed library (and in deployment as a separately built wheel in the image), not modified, and not linked
into Plimsoll's own source; under the LGPL that is the arrangement that keeps Plimsoll free to remain MIT.
If you redistribute a **container image or a bundled build** that includes it, keep its licence text with the
distribution and keep the library replaceable — the `web/deploy/` Dockerfile installs it as a normal
dependency, which satisfies that. The core calculation package (`tools/plimsoll`) does not depend on it at all.

## Data files

| file | status |
|---|---|
| `tools/plimsoll/cases/taylor_gertler_cr_table.json` | coefficient table parsed from a printed book — **source citation pending**, see below |
| `data/british_armour_standards_1908_1912.json` | armour-standards dataset — **source citation pending**, the file carries no provenance field |
| `tools/plimsoll/cases/damage_scenarios.json`, `generic_test_steamer_1910.json`, `damage_lab/*`, `projects/analytic_box.project.json`, `projects/generic_flooding_box.project.json`, `projects/generic_steamer.project.json`, `projects/damage-presets.json`, `templates/speed_power.html` | synthetic study material created for this project |
| historical-ship cases (Queen Mary) | **not included** in this repository, by decision: the ship's case data and the tests anchored on it stay in the author's private repository |

### Two citations that must be added before publication

1. `taylor_gertler_cr_table.json` — the printed source (author, title, edition, page) of the Taylor–Gertler
   residual-resistance table.
2. `data/british_armour_standards_1908_1912.json` — the published standards or documents the dataset was
   compiled from.

Neither is a code dependency; both are factual data compiled by the author, but citing the sources is the
honest thing to do and the file names give no clue.
