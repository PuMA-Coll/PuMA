# PuMA Pipeline

Data-processing scripts used by the Pulsar Monitoring in Argentina (PuMA)
group at the Argentinian Institute of Radioastronomy (IAR). The monitoring
program regularly observes glitching pulsars and MSPs used for
gravitational-wave searches. The current compatibility target is Python 2 with
the pulsar software installed by `puma-docker`.

PRESTO performs the principal folding work. Tempo2 produces and analyzes TOAs.

Includes:

1. Configuration files for pulsar software.
2. `puma_process.py`: moves uploaded observations and selects a pipeline.
3. `pipe_reduc.py`: reduction pipeline for configured millisecond pulsars.
4. `pipe_pugliS.py`: reduction pipeline including glitch searches.
5. `puma_toa.py`: TOA extractor.
6. `looper.py`: loops over data folders.
7. `puma_template.py`: creates timing templates.
8. Notebook tools for different subjects.

## Pipeline Routing

`puma_process.py` is the dispatcher and should be the entrypoint for future
scheduled execution. It requires canonical J catalog names. B-name inputs are
rejected with a message requesting the corresponding J name.

The current MSP list is stored in `config/pulsars.ini`:

- `J0437-4715`
- `J2241-5236`

MSPs use `pipe_reduc.py`, which does not perform glitch searches. The registry
also records `J1744-1134` and `J1810-197` as non-MSPs, which use
`pipe_pugliS.py`. Unknown J names are rejected until their registry entry and
`.ini`, `.par`, and `.pfd.std` assets are verified. Adding an MSP should be a
configuration change, not a code change. The full supported pulsar inventory
still needs to be checked against the cluster.

## Observation Lifecycle

New observations arrive as multi-GB `.fil` files in a dedicated input-folder
tree. `puma_process.py` discovers observation folders, moves ready inputs into
the processing layout, and selects the appropriate pipeline.

An observation folder may be visible while its `.fil` file is still being
written. Automatic processing must therefore wait for an explicit completion
signal or confirm that file size and modification time remain stable for a
defined interval. That readiness policy has not yet been implemented.

After all processing and local product publication succeed, raw `.fil` files
are moved to a separate staging folder for transfer to the storage cluster by
Globus. Globus controls transfer verification and source-copy retention.
Failed, incomplete, unsupported, or unknown observations should instead be
quarantined with a reason while later ready observations continue processing.

Pipeline products remain local, including JSON observation metadata, PFDs,
PNG plots, `.tim` files, residuals, and masks. The internal PuGli-S website
displays selected products. Operational `.par` files and other timing assets
may be maintained on the IAR cluster rather than in Git.

## Future Automation

No scheduler is enabled by this repository yet. A future host or service
scheduler should invoke `puma_process.py` when the processing system is idle
and stable observations are waiting. Hourly polling is a reasonable initial
estimate, not a fixed cadence. Automation requires a single-instance lock,
readiness checks, duplicate-observation protection, quarantine, retries,
durable logs, and failure alerts.

## Validation

A planned glitch-path validation uses a short J0835-4510 (Vela) observation.
PRESTO should independently recover the correct period; a deliberately
outdated test `.par` file can then verify that the glitch trigger activates.
The outdated file is for validation only and must not replace operational
timing assets.
