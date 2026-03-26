# Installer Guide

> After all, why not? Why not have one script to rule them all?

This document describes only `install_pulsar_stack.sh`: what it installs, where it downloads from, which local source patches it applies, and which observatory codes and coordinates are used.

## Purpose

`install_pulsar_stack.sh` builds and installs the local pulsar software stack under a user-controlled prefix without `sudo`.

Default locations:

- `PSRHOME="$HOME/pulsar"`
- `PREFIX="$HOME/pulsar/install"`
- `PRESTO_VENV="$PREFIX/presto-venv"`
- `PYTOOLS_VENV="$PREFIX/python-tools-venv"`

By default the script installs into:

- binaries: `$PREFIX/bin`
- libraries: `$PREFIX/lib`
- headers: `$PREFIX/include`
- PRESTO Python env: `$PREFIX/presto-venv`
- Python tools env for PINT/rficlean: `$PREFIX/python-tools-venv`

## Docker Wrapper

This repository also includes Docker helpers around the installer:

- `docker_install.sh`
  - builds `Dockerfile.pulsar`
  - runs `install_pulsar_stack.sh` inside the image
  - installs the stack under `/opt/pulsar`
- `docker_run.sh`
  - starts the image with useful bind mounts and host user mapping

Typical use:

```bash
./docker_install.sh --no-cache
./docker_run.sh
```

Default Docker paths:

- `PSRHOME=/opt/pulsar`
- `PREFIX=/opt/pulsar/install`
- current host directory mounted at `/data`
- host home mounted at `/host_home`

By default `docker_run.sh`:

- mounts `"$PWD"` at `/data`
- mounts `"$HOME"` at `/host_home`
- sets the working directory to `/data`
- runs as the host UID:GID
- starts `/bin/bash`

## What It Installs

The script can install:

- `PSRDADA`
- `PGPLOT`
- `PSRCHIVE`
- `DSPSR`
- `PRESTO`
- `PINT`
- `clfd`
- `RFIClean`
- `SIGPROC`
- `TEMPO`
- `TEMPO2`

Each component can be skipped with the corresponding `--skip-*` flag.

## Upstream Sources

By default the script pulls from these upstream locations:

- `PSRDADA`
  - `git://git.code.sf.net/p/psrdada/code`
- `PSRCHIVE`
  - `git://git.code.sf.net/p/psrchive/code`
- `PGPLOT`
  - `ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz`
- `DSPSR`
  - `git://git.code.sf.net/p/dspsr/code`
- `PRESTO`
  - `https://github.com/scottransom/presto.git`
- `PINT`
  - `https://github.com/nanograv/PINT.git`
- `clfd`
  - `https://github.com/v-morello/clfd.git`
- `RFIClean`
  - `https://github.com/ymaan4/RFIClean.git`
- `SIGPROC`
  - `https://github.com/SixByNine/sigproc.git`
- `TEMPO`
  - `git://git.code.sf.net/p/tempo/tempo`
- `TEMPO2`
  - `https://bitbucket.org/psrsoft/tempo2.git`

Most of these can be overridden with `--*-repo` or `--*-src`.

For the containerized path, the build recipe comes from:

- `Dockerfile.pulsar`

## Build Method By Component

- `PSRDADA`
  - `./bootstrap`
  - `./configure --prefix="$PREFIX"`
  - `make`
  - `make install`

- `PGPLOT`
  - downloaded as source tarball
  - configured through local `sys_linux/*.conf`
  - built with `make`
  - static libraries copied into `$PREFIX/lib`

- `PSRCHIVE`
  - `./bootstrap`
  - `SWIG=/usr/bin/swig ./configure --enable-shared --prefix="$PREFIX"`
  - `make`
  - `make install`
  - then builds `More/python` into `PRESTO_VENV` with:
    - `SWIG_FLAGS="-c++ -Wall -python -I../../local_include -I../.."`
    - `CPPFLAGS="-I<venv-python-include> -I<numpy-include> ..."`
    - `pythondir=<PRESTO_VENV site-packages>`
  - pins `numpy<2` in `PRESTO_VENV` before building `_psrchive`
  - expected runtime Python imports from `PRESTO_VENV`:
    - `from presto import sigproc, rfifind`
    - `import psrchive`

- `DSPSR`
  - writes `backends.list`
  - `./bootstrap`
  - `./configure --prefix="$PREFIX"`
  - `make`
  - `make install`

- `PRESTO`
  - source patching first
  - builds with one of:
    - `meson`
    - top-level `Makefile`
    - `src/Makefile`
  - Python package installed in `PRESTO_VENV`

- `PINT`
  - cloned from source
  - source/runtime data patching first
  - installed with:
    - `pip install .`
  - installed into `PYTOOLS_VENV`

- `clfd`
  - cloned from source
  - installed with:
    - `pip install .`
  - installed into `PYTOOLS_VENV`
  - depends on the PSRCHIVE Python bindings being available first

- `RFIClean`
  - cloned from source
  - source patching first
  - built with:
    - `make`
    - `make install`
  - installs `rficlean` into `$PREFIX/bin`

- `SIGPROC`
  - cloned from source
  - source patching first
  - built with:
    - `./bootstrap`
    - `./configure --prefix="$PREFIX"`
    - `make`
    - `make install`

- `TEMPO`
  - `autoreconf --install`
  - `./configure --prefix="$PREFIX"`
  - `make`
  - `make install`
  - runtime files copied to `$PREFIX/tempo`
  - observatory data rewritten after install in `$PREFIX/tempo/obsys.dat`

- `TEMPO2`
  - `./bootstrap`
  - `./configure --prefix="$PREFIX"`
  - `make`
  - `make install`
  - `make plugins`
  - `make plugins-install`
  - `T2runtime` copied to `$PREFIX/share/tempo2`
  - observatory data rewritten after install in `$PREFIX/share/tempo2/observatory/observatories.dat`

## Local Source Patches Applied

The installer is not a plain upstream build. It applies local patches for observatory IDs, aliases, machine IDs, and a few build-compatibility fixes.

Important distinction:

- `PRESTO`, `DSPSR`, `SIGPROC`, and `PINT` have IAR observatory mappings hardcoded in source-controlled files that are patched before build/install.
- `TEMPO` and `TEMPO2` use runtime observatory data files, not compile-time baked tables for site coordinates. Their installed `.dat` files are rewritten after install because the binaries read those files when they run.

### PRESTO

Patched files:

- `$PSRHOME/presto/src/sigproc_fb.c`
- `$PSRHOME/presto/src/polycos.c`
- `$PSRHOME/presto/src/misc_utils.c`
- `$PSRHOME/presto/python/presto/sigproc.py`
- `$PSRHOME/presto/python/presto/polycos.py`
- `$PSRHOME/presto/bin/dat2tim.py`
- `$PSRHOME/presto/bin/guppidrift2fil.py`
- `$PSRHOME/presto/bin/get_TOAs.py`

Changes:

- add local telescope IDs and aliases
- add local machine IDs
- add TEMPO code mappings for the local observatories

### DSPSR

Patched file:

- `$PSRHOME/dspsr/Kernel/Formats/sigproc/SigProcObservation.C`

Changes:

- add local telescope ID to telescope-name mapping
- add local ITOA code to SIGPROC ID mapping
- add local machine ID to machine-name mapping

### SIGPROC

Patched file:

- `$PSRHOME/sigproc/src/aliases.c`
  - or `$PSRHOME/sigproc/aliases.c` for old flat layouts

Changes:

- add local telescope ID to telescope-name mapping
- add TEMPO one-character observatory code mapping
- add local machine ID to backend-name mapping

Additional build-compatibility fixes are also applied when needed, for example to old C/Fortran sources and generated header handling.

### PINT

Patched file:

- current layout:
  - `$PSRHOME/PINT/src/pint/data/runtime/observatories.json`
- legacy fallback:
  - `$PSRHOME/PINT/src/pint/observatory/observatories.py`

Changes:

- add local observatory names
- add aliases
- add TEMPO one-character codes
- add ITOA-style two-character codes
- add ITRF coordinates for the local observatories

### TEMPO

Runtime file patched or rewritten:

- `$PREFIX/tempo/obsys.dat`

Policy:

- this installer is intentionally IAR-first
- when local TEMPO one-character observatory codes conflict with upstream entries, the conflicting upstream entries are removed before the local IAR entries are inserted
- in the current local mapping, `m`, `r`, and `s` are reserved for `IAR1`, `IAR1R`, and `IAR2R`
- that means stock `MEERKAT`, `GMRT`, and `SHAO 65m XYZ` entries do not survive in the installed `obsys.dat`
- inside the Docker image, the `/opt/pulsar` tree is typically owned by `root`; rerunning this installer there from the non-root shell provided by `./docker_run.sh` can fail on autotools cache writes or similar build-step updates
- for in-container rebuilds or patch refreshes, run the installer from a root shell in the image
- this file is used by TEMPO at runtime
- it is not compiled into the TEMPO binary

### TEMPO2

Runtime file patched or rewritten:

- `$PREFIX/share/tempo2/observatory/observatories.dat`

Notes:

- this file is used by TEMPO2 at runtime
- it is not compiled into the TEMPO2 binary

### RFIClean

RFIClean is not patched for observatory coordinates or timing codes. The installer only applies source/build compatibility fixes when needed so it builds on a modern compiler and linker setup.

## Observatory Codes Used

These are the local observatory IDs and aliases used across the stack.

Telescope IDs:

- `IAR1 = 19`
- `IAR2 = 20`
- `IAR1R = 21`
- `IAR2R = 22`
- `DSA3 = 24`
- `CLTC = 25`

Aliases and TEMPO one-character codes:

- `IAR1 -> A1 -> m`
- `IAR2 -> A2 -> o`
- `IAR1R -> R1 -> r`
- `IAR2R -> R2 -> s`
- `DSA3 -> D3 -> p`
- `CLTC -> CL -> q`

IAR-first overlap policy:

- `m` is owned locally by `IAR1`
- `r` is owned locally by `IAR1R`
- `s` is owned locally by `IAR2R`
- the installer removes conflicting upstream `TEMPO` entries before writing these local mappings

Machine IDs:

- `RTL_Filterbank = 23`
- `IAR_ROACH_v1 = 24`
- `IAR_SNAP_v1 = 25`

## Coordinates Used

The local IAR site coordinates used in the stack are:

- `IAR1 / IAR1R`
  - `(2765357.08, -4449628.98, -3625726.47)` m
- `IAR2 / IAR2R`
  - `(2765322.49, -4449569.52, -3625825.14)` m
- `DSA3`
  - `(1822902.736, -4849284.620, -3708078.704)` m
- `CLTC`
  - `(1704386.809, -4721089.389, -3922212.645)` m

Coordinate conventions used by patched files:

- `TEMPO` `obsys.dat`
  - uses TEMPO's traditional packed observatory format
  - values are geodetic latitude, geodetic longitude, and elevation
- `TEMPO2` `observatories.dat`
  - uses geocentric ITRF XYZ coordinates in meters
- `PINT`
  - uses geocentric ITRF XYZ coordinates in meters in `observatories.json`
- local analysis scripts in this repository
  - use geocentric ITRF XYZ coordinates in meters

Same observatories in both conventions:

| Observatory | TEMPO `obsys.dat` lat / lon / elev | Geocentric ITRF XYZ (m) |
|---|---|---|
| `IAR1` / `IAR1R` | `-345159.0   580823.5   10.` | `(2765357.08, -4449628.98, -3625726.47)` |
| `IAR2` / `IAR2R` | `-345202.9   580823.4   10.` | `(2765322.49, -4449569.52, -3625825.14)` |
| `DSA3` | `-354633.1   692353.7   800.` | `(1822902.736, -4849284.620, -3708078.704)` |
| `CLTC` | `-381129.1   700858.4   800.` | `(1704386.809, -4721089.389, -3922212.645)` |

Important:

- `SIGPROC` does not carry observatory coordinates in the local flow
- coordinates are maintained in:
  - `TEMPO` `obsys.dat`
  - `TEMPO2` `observatories.dat`
  - local analysis programs such as `line_analysis_spc.py` and `continuum_analysis_spc.py`

## Shell Environment Written By The Installer

The installer updates `~/.bashrc` with a `pulsar-stack` block that exports:

- `PSRHOME`
- `PREFIX`
- `PRESTO_VENV`
- `PYTOOLS_VENV`
- `PATH="$PYTOOLS_VENV/bin:$PRESTO_VENV/bin:$PREFIX/bin:$PATH"`
- `LD_LIBRARY_PATH`
- `CPATH`
- `LIBRARY_PATH`
- `PKG_CONFIG_PATH`
- `PGPLOT_DIR`
- `PRESTO`
- `TEMPO`
- `TEMPO2`

## Debian/Ubuntu Prerequisites

Install these first:

```bash
sudo apt update
sudo apt install -y \
  build-essential gfortran git autoconf automake libtool libtool-bin pkg-config tar \
  python3 python3-venv python3-pip python3-dev swig \
  libglib2.0-dev libfftw3-dev libgsl-dev libcfitsio-dev libpng-dev \
  libx11-dev libxt-dev \
  m4 perl flex bison
```

If you want to build the Docker image too, also install Docker on the host:

```bash
sudo apt install -y docker.io
sudo systemctl enable --now docker
```

## Notes About Portability

The script is user-portable because it defaults to `$HOME/pulsar` and `$HOME/pulsar/install`, not a fixed username path.

It is still mainly Linux-oriented:

- PGPLOT/X11 handling is oriented toward Unix-like systems
- package assumptions are closest to Debian/Ubuntu
- several upstream packages are old and require compatibility fixes

So it is suitable for similar Linux machines, but it should still be considered a site-local installer rather than a universally portable one.
