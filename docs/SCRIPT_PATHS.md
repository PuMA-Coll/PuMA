# Script Path Inventory

This document summarizes the main filesystem locations accessed by the Python
scripts in this repository.

## Absolute Roots

- `/opt/pulsar/`
- `/opt/pulsar/PyPulse/pypulse/`
- `/opt/pulsar/puma/scripts/`
- `/opt/pulsar/puma/pardir/`
- `/opt/pulsar/puma/config/`
- `/opt/pulsar/puma/config/timing/`
- `/opt/pulsar/tempo/tzpar/`
- `/home/jovyan/work/scratch_4/observacion/upload/`
- `/home/jovyan/work/scratch_4/observacion`
- `/home/jovyan/work/shared/`
- `/home/jovyan/work/shared/PuGli-S/`
- `/home/jovyan/work/shared/Data/J0437-4715/Prueba_rficlean/A1/con_rficlean`
- `/home/observacion/scratchdisk/PuGli-S/`
- `/home/observacion/scratchdisk/PuGli-S/puglieseweb/`

## Derived Relative Folders

- Current working directory via `os.getcwd()` or `os.environ['PWD']`
- `temp/`
- `tmp/`
- `original/`
- `ATNF_pars/`
- `no_tan_malas/`
- `last_obs/`
- `tims/`
- `<PSR>/pngs/`
- `<PSR>/pfds/`
- `<dest_path>/<pulsar_name>/`
- `obs0/`, `obs1/`, ...

## Per-Script Summary

| Script | Reads From | Writes To |
| --- | --- | --- |
| `scripts/puma_lib.py` | observation folder, `/opt/pulsar/puma/pardir/`, `/opt/pulsar/puma/config/`, per-observation `*.fil`, `*.mask`, `*.pfd` | observation folder, `original/`, `tmp/`, timing file path passed in |
| `scripts/pipe_reduc.py` | observation folder, par directory argument, `/home/jovyan/work/shared/PuGli-S/` | `/home/jovyan/work/shared/PuGli-S/tims/`, `<PuGli-S>/<PSR>/`, `<PuGli-S>/last_obs/` |
| `scripts/pipe_pugliS.py` | observation folder, par directory argument, `/home/jovyan/work/shared/PuGli-S/` | `/home/jovyan/work/shared/PuGli-S/tims/`, `<PuGli-S>/<PSR>/`, `<PuGli-S>/last_obs/` |
| `scripts/puma_process.py` | `/home/jovyan/work/scratch_4/observacion/upload/` by default | `/home/jovyan/work/scratch_4/observacion` by default, plus per-observation `obsN/` folders |
| `scripts/puma_reprocess.py` | current working directory tree | `temp/`, `/home/jovyan/work/shared/` |
| `scripts/puma_utils.py` | observation folder, `*.png`, `*.pfd`, `*.polycos`, `*mask*.ps` | `<path2end>/last_obs/`, `<path2end>/<PSR>/pngs/`, `<path2end>/<PSR>/pfds/`, moved observation folders |
| `scripts/puma_timing.py` | par file path, tim file path | output directory, optional `/home/jovyan/work/shared/PuGli-S/last_obs/` |
| `scripts/puma_toa.py` | current working directory by default, par dir argument | timing directory argument or current working directory |
| `scripts/puma_reduc.py` | current working directory by default, par dir argument | observation folder outputs |
| `scripts/pipe_red_trigger.py` | current working directory by default, par dir argument | observation folder outputs |
| `scripts/puma_template.py` | current working directory tree, discovered `*.pfd` files | generated `.std` template in current working directory |
| `scripts/puma_select_pfds.py` | current working directory `*.pfd`, matching `.polycos`, `.bestprof` | `no_tan_malas/` |
| `scripts/convert_tcb2tdb.py` | current working directory `*.par` files | modified `.par` files, `ATNF_pars/`, `temp.par` |
| `scripts/puma_rficlean.py` | `2020-07*A1/obs*` folders, `.fil` files | cleaned files in those folders, `/home/jovyan/work/shared/Data/J0437-4715/Prueba_rficlean/A1/con_rficlean` |
| `scripts/puma_log.py` | current working directory `*.fil`, `*.pfd`, `*.mask`, `/opt/pulsar/`, `/opt/pulsar/PyPulse/pypulse/` | pulsar log table at configured destination |
| `scripts/looper.py` | current working directory subfolders | whatever the invoked child script writes |
| `puglieseweb/puglieseweb_update.py` | `/home/observacion/scratchdisk/PuGli-S/`, `/home/observacion/scratchdisk/PuGli-S/puglieseweb/`, per-pulsar JSON and image folders | `by_psr.html`, `last_obs.html`, per-pulsar HTML files, generated thumbnails |
| `puglieseweb/get_mjd_now.py` | none beyond runtime environment | stdout only |
| `puma_cat/puma_cat.py` | workbook/config data in repo | generated `.sh`, `.iar`, `.par`, `.ini` files in current working directory |

## Notes

- Many scripts assume they are executed from the observation folder they operate on.
- Several helper scripts only use relative paths, so their real read/write targets depend on the caller's current working directory.
- `scripts/backup/puma_lib.py` is a backup copy and should not be treated as an active entrypoint.
