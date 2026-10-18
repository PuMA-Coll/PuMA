# PuMA Repository Guidance

## Purpose

PuMA is the pulsar-observation processing pipeline used by the Pulsar
Monitoring in Argentina (PuMA) group at the Argentinian Institute of
Radioastronomy (IAR). It is tightly coupled to the software and paths installed
by `puma-docker`.

The monitoring program has two main source classes:

- Glitching pulsars, whose regular observations are folded and searched for
  changes in rotational behavior.
- Millisecond pulsars (MSPs), whose timing products support gravitational-wave
  searches and which do not use the glitch-search path.

PRESTO performs the principal folding work. Tempo2 and related tools produce
and analyze times of arrival (TOAs). Do not describe the timing path as Tempo 1
unless code inspection demonstrates an intentional Tempo 1 operation.

## Observation Lifecycle

- New multi-GB `.fil` observations arrive in a dedicated input area, normally
  with one observation represented by a folder.
- Files may still be written while a scheduled scan is running. Never process
  an observation merely because its folder exists.
- A future scheduler must require a readiness signal or a verified stability
  interval in which relevant file sizes and modification times do not change.
  The exact interval and acquisition-system signal are not yet defined.
- Processing should run when the processing system is idle and at least one
  ready observation is available. Hourly polling is only a provisional option,
  not a fixed requirement.
- `puma_process.py` is the dispatcher. Successfully processed raw `.fil` files
  move to a separate staging area to await Globus transfer to the storage
  cluster. Globus owns transfer verification and the decision to retain or
  remove its source copy; PuMA must not duplicate that policy.
- A failed, unknown, incomplete, or unsupported observation should be
  quarantined with a reason while processing continues for other ready
  observations. Do not let one bad observation stop the full scheduled batch.
- Do not move raw data to the Globus staging area until all required pipeline
  stages and local product publication have succeeded.

## Products and Ownership

- Raw `.fil` data are ultimately stored on a separate cluster through Globus.
- Pipeline products remain local. These include observation JSON metadata,
  PFDs, PNG plots, `.tim` files, residual products, masks, and related web
  products.
- The internal PuGli-S website consumes selected local products. Preserve its
  paths and product conventions unless a coordinated website change is made.
- Operational timing assets, including updated `.par` files, may exist outside
  Git and on the IAR cluster. Absence from this checkout does not establish
  that an asset does not exist operationally.

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
- No representative `.fil` input is currently available in this workspace, so
  scientific end-to-end validation remains pending.
- Validate modified scripts with the image's Python 2.7 runtime. Static checks
  and CLI smoke tests do not establish scientific correctness.

## Current Pending Verification

- Obtain an authorized disposable `.fil`. A short J0835-4510 (Vela) observation
  is the preferred glitch-path validation input.
- Run a narrow, non-destructive operation and record inputs, commands,
  environment, outputs, and return codes.
- Compare results with a known-good reference where available.
- Confirm whether future J0835-4510 data maps to the tracked B0833-45
  configuration and obtain matching timing assets.
- Check the complete cluster inventory of pulsar folders, `.par` files, and
  timing assets, then complete `config/pulsars.ini`.
- Add focused tests when functionality is actively used, especially for the
  future glitch-alert path.
- For validation only, use a deliberately outdated Vela `.par` file after
  independently deriving the correct period with PRESTO. Verify that the
  configured discrepancy triggers the expected glitch alert. Keep this test
  asset isolated from operational timing files.

## Planned Upgrades

- Perform a separately validated Python 3/runtime migration if current
  upstream dependencies support it. Do not upgrade dependencies blindly.
- Introduce staged logging and error handling: per-observation context,
  consistent library errors, narrow exception handling, subprocess reporting,
  and alert delivery separated from reduction logic.
- `puma_process.py` is the dispatcher. It routes
  canonical J-name pulsars through `config/pulsars.ini`. The current MSPs are
  J0437-4715 and J2241-5236, and they use `pipe_reduc.py` without glitch
  searches. J1744-1134 and J1810-197 are currently recorded as non-MSPs;
  other J-name pulsars require registry and asset verification before use.
- After the input contract is validated, schedule `puma_process.py` when the
  system is idle and ready observations exist. A host/service scheduler may
  poll approximately hourly or several times per day, but should skip work when
  no stable input is available. The design must include a single-instance lock,
  readiness/stability checks, retry/backoff, quarantine, durable logs, failure
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
