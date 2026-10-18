# PuMA Pipeline

Data-processing scripts for pulsar observations at IAR. The current
compatibility target is Python 2 with the standard pulsar software installed by
`puma-docker`.

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

MSPs use `pipe_reduc.py`, which does not perform glitch searches. Other J-name
pulsars use `pipe_pugliS.py`. Adding an MSP should be a configuration change,
not a code change.

## Future Automation

No scheduler is enabled by this repository yet. A future host or service
scheduler should invoke `puma_process.py` approximately hourly, with locking,
duplicate-observation protection, retries, durable logs, and failure alerts.
