# puma_pipe

PuMA is a pulsar observation processing toolkit used at IAR to ingest raw observations, run reduction pipelines, generate TOAs and timing products, and publish derived outputs into the PuGli-S database and web layout.

The repository now targets Python 3 for the Python scripts. Runtime functionality still depends on the local pulsar software stack being installed separately.

The current working Python environment used for this repo is the PRESTO virtual environment at `/home/USER/pulsar/install/presto-venv/`.

## What This Repo Does

At a high level, the repository supports this workflow:

1. New observations arrive in an upload directory.
2. The observations are reorganized into a per-pulsar folder structure.
3. A reduction pipeline is selected depending on the pulsar type.
4. PRESTO and related external tools generate masks, folded products, TOAs, and timing plots.
5. Selected products are copied into the PuGli-S database layout.
6. Static web pages can be regenerated from the database content.

## Main Script Groups

### 1. Observation ingestion and dispatch

- [`scripts/puma_process.py`](/home/USER/proyectos/PuMA/scripts/puma_process.py)
  Main ingestion entrypoint.
  It scans an upload folder, moves each observation into the reduction tree, and dispatches either the stable timing pipeline or the glitch-search pipeline.

- [`scripts/puma_reprocess.py`](/home/USER/proyectos/PuMA/scripts/puma_reprocess.py)
  Reorganizes older observation layouts into the newer format and then reprocesses them through `puma_process.py`.

- [`scripts/puma_utils.py`](/home/USER/proyectos/PuMA/scripts/puma_utils.py)
  Shared helper functions for:
  - moving observation folders into the per-pulsar database tree
  - copying PNG, PFD, and polycos outputs into the PuGli-S layout
  - writing observation metadata into JSON files

### 2. Reduction and timing pipelines

- [`scripts/puma_reduc.py`](/home/USER/proyectos/PuMA/scripts/puma_reduc.py)
  Single-folder reduction entrypoint.
  It instantiates an `Observation`, loads reduction parameters from the pulsar config, and runs a PRESTO folding workflow.

- [`scripts/pipe_reduc.py`](/home/USER/proyectos/PuMA/scripts/pipe_reduc.py)
  Stable pulsar timing pipeline.
  It reduces an observation, calculates S/N, generates TOAs, copies outputs into PuGli-S, and generates timing residual plots.

- [`scripts/pipe_pugliS.py`](/home/USER/proyectos/PuMA/scripts/pipe_pugliS.py)
  Glitch-monitoring pipeline.
  It performs glitch search logic, calculates S/N and TOAs, copies outputs into PuGli-S, and generates residual plots oriented toward glitch-tracked pulsars.

- [`scripts/pipe_red_trigger.py`](/home/USER/proyectos/PuMA/scripts/pipe_red_trigger.py)
  Lightweight glitch trigger.
  It runs the glitch-detection logic and reports whether a red alert condition is present.

- [`scripts/puma_toa.py`](/home/USER/proyectos/PuMA/scripts/puma_toa.py)
  TOA generation entrypoint around the `Observation.do_toas()` workflow.

- [`scripts/puma_timing.py`](/home/USER/proyectos/PuMA/scripts/puma_timing.py)
  Residual generation and plotting utility.
  It reads a `.par` and `.tim`, computes residuals with `libstempo`, writes a `.res` file, and saves a timing plot.

### 3. Shared reduction logic

- [`scripts/puma_lib.py`](/home/USER/proyectos/PuMA/scripts/puma_lib.py)
  This is the central operational module in the repo.
  It defines the `Observation` class and most of the shared pipeline behavior:
  - reading observation metadata from `.fil` headers
  - reading pulsar reduction parameters from config files
  - creating RFI masks with `rfifind`
  - optionally cleaning data with `rficlean`
  - preparing and running `prepfold`
  - reading `bestprof` outputs
  - performing glitch search logic
  - generating TOAs
  - computing mask quality metrics
  - calculating S/N from folded products

## Supporting utilities

These scripts are not the main reduction entrypoints, but they support common operations around the pipeline.

- [`scripts/puma_template.py`](/home/USER/proyectos/PuMA/scripts/puma_template.py)
  Selects the highest-S/N folded observation in the current tree and generates a smoothed `.std` template.

- [`scripts/puma_select_pfds.py`](/home/USER/proyectos/PuMA/scripts/puma_select_pfds.py)
  Filters low-S/N folded products by moving them into a side folder.

- [`scripts/convert_tcb2tdb.py`](/home/USER/proyectos/PuMA/scripts/convert_tcb2tdb.py)
  Converts `.par` files from TCB to TDB using `tempo2`, keeping backup copies in `ATNF_pars/`.

- [`scripts/fil_corrector.py`](/home/USER/proyectos/PuMA/scripts/fil_corrector.py)
  Rewrites timing/header information for filterbank files.

- [`scripts/puma_log.py`](/home/USER/proyectos/PuMA/scripts/puma_log.py)
  Builds observation log rows from `.fil`, `.mask`, and `.pfd` products.

- [`scripts/puma_rficlean.py`](/home/USER/proyectos/PuMA/scripts/puma_rficlean.py)
  Batch helper for running `rficlean` across a set of folders and copying the cleaned results elsewhere.

- [`scripts/looper.py`](/home/USER/proyectos/PuMA/scripts/looper.py)
  Runs another script repeatedly across observation subfolders.

- [`scripts/all_templates.py`](/home/USER/proyectos/PuMA/scripts/all_templates.py)
  Batch helper for generating templates across pulsar folders.

- [`scripts/rename_files.py`](/home/USER/proyectos/PuMA/scripts/rename_files.py)
  Small filename rewriting helper.

- [`scripts/period.py`](/home/USER/proyectos/PuMA/scripts/period.py)
  Utility related to single-pulse or period-aligned file processing.

- [`scripts/concat.py`](/home/USER/proyectos/PuMA/scripts/concat.py)
  Concatenates/interpolates pulse tables for downstream analysis.

- [`scripts/fit_single_pulses.py`](/home/USER/proyectos/PuMA/scripts/fit_single_pulses.py)
  Analysis script for comparing or fitting extracted single-pulse data products.

- [`scripts/single_pulses.py`](/home/USER/proyectos/PuMA/scripts/single_pulses.py)
  Single-pulse analysis support code.

- [`scripts/waterfaller_puma.py`](/home/USER/proyectos/PuMA/scripts/waterfaller_puma.py)
- [`scripts/waterfaller_su.py`](/home/USER/proyectos/PuMA/scripts/waterfaller_su.py)
- [`scripts/waterfaller_su_plots_tesis.py`](/home/USER/proyectos/PuMA/scripts/waterfaller_su_plots_tesis.py)
- [`scripts/waterfaller_su_xtej1810.py`](/home/USER/proyectos/PuMA/scripts/waterfaller_su_xtej1810.py)
  Waterfall/dynamic-spectrum plotting utilities for different observing or analysis contexts.

## Catalog and web tools

- [`puma_cat/puma_cat.py`](/home/USER/proyectos/PuMA/puma_cat/puma_cat.py)
  Pulsar catalog/config helper.
  It uses ATNF-derived information to generate `.par`, `.ini`, `.iar`, and shell helper files.

- [`puglieseweb/puglieseweb_update.py`](/home/USER/proyectos/PuMA/puglieseweb/puglieseweb_update.py)
  Rebuilds the static PuGli-S HTML pages from the database content and image layout.

- [`puglieseweb/get_mjd_now.py`](/home/USER/proyectos/PuMA/puglieseweb/get_mjd_now.py)
  Small utility that prints the current UTC time and MJD.

## Data and configuration directories

- [`config`](/home/USER/proyectos/PuMA/config)
  Pulsar configuration, timing products, and installation reference files.

- [`config/timing`](/home/USER/proyectos/PuMA/config/timing)
  Timing templates and related standard profile files used by TOA generation and timing plots.

- [`pardir`](/home/USER/proyectos/PuMA/pardir)
  Pulsar parameter files used by parts of the reduction workflow.

- [`puglieseweb`](/home/USER/proyectos/PuMA/puglieseweb)
  Static site assets and generated HTML fragments for PuGli-S.

- [`test`](/home/USER/proyectos/PuMA/test)
  Sample artifacts that are useful for local checks or smoke-style validation.

- [`ipynb`](/home/USER/proyectos/PuMA/ipynb)
  Notebooks for analysis and one-off utilities.

## External software expected by the scripts

The scripts assume that several command-line tools are available on the host environment, including:

- `prepfold`
- `rfifind`
- `rficlean`
- `readfile`
- `pat`
- `tempo2`
- `psredit`
- `psrstat`
- `psrsmooth`
- ImageMagick `convert`

Some scripts also expect Python bindings or modules such as:

- `numpy`
- `pandas`
- `scipy`
- `matplotlib`
- `astropy`
- `psrchive`
- `libstempo`
- `sigproc`
- `rfifind`
- `psrqpy` for catalog generation

## Documentation

1. [docs/SCRIPT_PATHS.md](/home/USER/proyectos/PuMA/docs/SCRIPT_PATHS.md)
   Inventory of filesystem paths and folders accessed by the scripts, including copy and move destinations.

2. [pulsar_sw/INSTALLER.md](/home/USER/proyectos/PuMA/pulsar_sw/INSTALLER.md)
   Installation guide for the pulsar software environment and related dependencies.

## Tests

1. [`tests/test_smoke_scripts.py`](/home/USER/proyectos/PuMA/tests/test_smoke_scripts.py)
   Smoke tests for path-handling and file-move behavior in the main scripts, using mocks so PRESTO and PSRCHIVE do not need to be installed.

2. Run the smoke suite with:

```bash
python -m unittest discover -s tests -v
```

## Notes

- Many scripts still assume the IAR filesystem layout and default institutional paths.
- Several helpers are intended to be run from a specific working directory rather than imported as general-purpose libraries.
- Functional success still depends on the local pulsar stack being installed and compatible with the chosen runtime environment.
