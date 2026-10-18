# PuMA Repository Guidance

## Purpose

PuMA is a legacy pulsar-observation processing pipeline. It is tightly coupled
to the software and paths installed by `puma-docker`.

## Runtime Compatibility

- The supported compatibility target is currently Python 2.7 with PRESTO,
  PSRCHIVE, SIGPROC, Tempo/Tempo2, and the bundled scientific packages.
- Python 3 may now support some or all of the latest upstream software, but
  that has not been established for this pipeline. Treat a Python 3 migration
  as a separate project requiring dependency analysis, syntax conversion,
  scientific reference data, and end-to-end comparison.
- Do not use f-strings or Python-3-only syntax in legacy scripts. Prefer clear
  inline messages; use simple concatenation or `.format()` where Python 2
  compatibility requires it.

## Working Rules

- Work on the `agent` branch or another explicitly isolated branch.
- Inspect `git status` before editing and do not discard existing changes.
- Do not stage or commit unless the user explicitly requests it.
- Preserve scientific algorithms, defaults, channel selections, file formats,
  and output conventions unless a change is justified and validated.
- Do not run destructive reprocessing against irreplaceable observations.
- No representative `.fil` input is currently available, so scientific
  end-to-end validation remains pending.
- Validate modified scripts with the image's Python 2.7 runtime. Static checks
  and CLI smoke tests do not establish scientific correctness.

## Current Pending Verification

- Obtain an authorized disposable `.fil`, preferably for J0437-4715.
- Run a narrow, non-destructive operation and record inputs, commands,
  environment, outputs, and return codes.
- Compare results with a known-good reference where available.
- Confirm whether future J0835-4510 data maps to the tracked B0833-45
  configuration and obtain matching timing assets.
- Add focused tests when functionality is actively used, especially for the
  future glitch-alert path.

## Planned Upgrades

- Perform a separately validated Python 3/runtime migration if current
  upstream dependencies support it. Do not upgrade dependencies blindly.
- Introduce staged logging and error handling: per-observation context,
  consistent library errors, narrow exception handling, subprocess reporting,
  and alert delivery separated from reduction logic.
- Define a real `puma_pipe` dispatcher. The repository currently has no
  `puma_pipe.py`; the operational entrypoints are `pipe_reduc.py`,
  `pipe_pugliS.py`, and `pipe_red_trigger.py`.
- After the dispatcher and input contract are defined, schedule it approximately
  hourly or several times per day using a host/service scheduler. The design
  must include a single-instance lock, retry/backoff, durable logs, failure
  alerts, and protection against processing the same observation twice.
- Validate scheduling first with a dry-run or disposable input before enabling
  automatic scientific processing.

## Validation Limitations

- No executable test suite or complete scientific baseline is currently
  available.
- Legacy source contains mixed indentation and Python 2-only syntax; host
  Python 3 parsing is not authoritative.
- Never claim a pipeline or scheduling change is scientifically validated
  without representative data and a suitable reference.
