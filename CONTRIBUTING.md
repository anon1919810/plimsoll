# Contributing to Plimsoll

Thanks for looking. This is a small, deliberately conservative codebase: it computes numbers people may act on,
so the conventions below matter more than speed.

## Before you start

- **Licence**: contributions are accepted under the MIT Licence, the same as the project. By opening a pull
  request you agree to that.
- **Scope**: this repository is the general tool. Historical-ship case data, game/3D material and the
  development records live in a private repository and are not part of it.
- **Discussion first** for anything that changes a calculation, a method version or the meaning of an existing
  field: those are the changes that need agreement before code.

## Getting it running

```bash
# core: Python 3.12+, standard library only
python tools/plimsoll/run_all_tests.py
python tools/plimsoll/cli.py tools/plimsoll/cases/generic_test_steamer_1910.json

# web
cd web/frontend && npm ci
npm run test          # vitest
npm run build         # tsc -b && vite build — must stay at exit 0

cd ../backend && pip install -e '.[dev]'
pytest
```

Four core tests (`test_damage_lab`, `test_damage_lab_cli`, `test_damage_lab_vessel`, `test_fragmentation`) fail
where the package is not importable as `tools.plimsoll.*`. That is a pre-existing environment property, not a
regression to chase — run the suite in a way that makes the package importable, or ignore exactly those four.

## What a change has to satisfy

1. **The suite and the build.** `python tools/plimsoll/run_all_tests.py`, `npm run test`, `npm run build` and
   `npm run test` in the backend. No new failures.
2. **Numbers stay honest.** A new quantity carries `source` and `estimate`; an unknown stays unknown rather than
   becoming a zero or a plausible-looking default; a difference between two runs is only presented as a result
   when the two runs share their basis.
3. **Both languages.** User-facing strings live in the typed dictionaries (`web/frontend/src/i18n/*.ts`) and are
   added to **both** language blocks. A missing key renders as the key itself, on purpose — never add a string to
   one language only.
4. **Copy is passed, not reached for.** Pure helpers take the copy lookup as a parameter rather than importing a
   global, so the same result can be re-rendered in either language.
5. **Tests describe behaviour, not text.** Assert on states and numbers; do not snapshot whole pages.

## Style

- Match the file you are editing; the codebase is terse and comment-light, and comments explain *why* rather
  than what.
- Prefer small pure functions with an obvious name over configuration flags.
- If a claim in a comment can be measured, measure it and record the measurement.

## Reporting a problem

Open an issue with the command you ran, the input case, what you expected and what you got. **Do not paste
credentials** — if something looks like a leaked secret, describe where it is instead.
