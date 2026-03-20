#!/usr/bin/env bash
set -euo pipefail

usage() {
  cat <<'EOF'
Usage: install_pulsar_stack.sh [options]

Build and install the user-space pulsar stack into $HOME/pulsar/install:
  - PSRDADA
  - PGPLOT
  - PSRCHIVE
  - DSPSR
  - PRESTO
  - PINT
  - rficlean
  - SIGPROC
  - TEMPO
  - TEMPO2

This script does not use sudo. It assumes the required build tools and base
libraries are already present on the system.

Options:
  --prefix <dir>           Install prefix (default: $HOME/pulsar/install)
  --psrhome <dir>          Source/work tree root (default: $HOME/pulsar)
  --psrdada-src <dir>      PSRDADA source tree override (default: <psrhome>/psrdada)
  --psrdada-repo <url>     PSRDADA git repo to clone if source is missing
  --psrchive-src <dir>     PSRCHIVE source tree override (default: <psrhome>/psrchive)
  --psrchive-repo <url>    PSRCHIVE git repo to clone if source is missing
  --pgplot-src <dir>       PGPLOT source tree override (default: <psrhome>/pgplot-src)
  --pgplot-url <url>       PGPLOT source tarball URL if source is missing
  --dspsr-src <dir>        DSPSR source tree override (default: <psrhome>/dspsr)
  --dspsr-repo <url>       DSPSR git repo to clone if source is missing
  --presto-src <dir>       PRESTO source tree override (default: <psrhome>/presto)
  --presto-repo <url>      PRESTO git repo to clone if source is missing
  --presto-venv <dir>      Python virtual environment for PRESTO helpers
                          (default: <prefix>/presto-venv)
  --pint-src <dir>         PINT source tree override (default: <psrhome>/PINT)
  --pint-repo <url>        PINT git repo to clone if source is missing
  --pytools-venv <dir>     Python virtual environment for PINT/rficlean
                          (default: <prefix>/python-tools-venv)
  --rficlean-src <dir>     rficlean source tree override (default: <psrhome>/rficlean)
  --rficlean-repo <url>    rficlean git repo to clone if source is missing
  --sigproc-src <dir>      SIGPROC source tree override (default: <psrhome>/sigproc)
  --sigproc-repo <url>     SIGPROC git repo to clone if source is missing
  --tempo-src <dir>        TEMPO source tree override (default: <psrhome>/tempo)
  --tempo-repo <url>       TEMPO git repo to clone if source is missing
  --tempo2-src <dir>       TEMPO2 source tree override (default: <psrhome>/tempo2)
  --tempo2-repo <url>      TEMPO2 git repo to clone if source is missing
  --skip-psrdada           Do not build/install PSRDADA
  --skip-pgplot            Do not build/install PGPLOT
  --skip-psrchive          Do not build/install PSRCHIVE
  --skip-dspsr             Do not build/install DSPSR
  --skip-presto            Do not build/install PRESTO
  --skip-pint              Do not install PINT
  --skip-rficlean          Do not install rficlean
  --skip-sigproc           Do not build/install SIGPROC
  --skip-tempo             Do not build/install TEMPO
  --skip-tempo2            Do not build/install TEMPO2
  --update-sources         Run git fetch/pull in existing source trees before build
  --clean                  Run make distclean or make clean before configuring
  --reclone-on-diverge     If a source tree cannot fast-forward, move it aside and reclone it
  --with-psrchive-plot     Request PSRCHIVE plotting support (default)
  --without-psrchive-plot  Disable PSRCHIVE plotting support
  --pgplot-dir <dir>       PGPLOT installation root for PSRCHIVE plotting support
                          (default: <psrhome>/pgplot)
  --jobs <n>               Parallel make jobs (default: nproc)
  --dspsr-backends <list>  Space-separated DSPSR backends.list content (default: dada)
  --help                   Show this help

Examples:
  ./install_pulsar_stack.sh
  ./install_pulsar_stack.sh --prefix $HOME/pulsar/install --jobs 8
  ./install_pulsar_stack.sh --skip-tempo2
EOF
}

PSRHOME="${HOME}/pulsar"
PREFIX="${HOME}/pulsar/install"
PSRDADA_SRC=""
PSRCHIVE_SRC=""
PGPLOT_SRC=""
DSPSR_SRC=""
PRESTO_SRC=""
PRESTO_VENV=""
PINT_SRC=""
PINT_REPO="https://github.com/nanograv/PINT.git"
PYTOOLS_VENV=""
RFICLEAN_SRC=""
RFICLEAN_REPO="https://github.com/ymaan4/RFIClean.git"
SIGPROC_SRC=""
TEMPO_SRC=""
TEMPO2_SRC=""
PSRDADA_REPO="git://git.code.sf.net/p/psrdada/code"
PSRCHIVE_REPO="git://git.code.sf.net/p/psrchive/code"
PGPLOT_URL="ftp://ftp.astro.caltech.edu/pub/pgplot/pgplot5.2.tar.gz"
DSPSR_REPO="git://git.code.sf.net/p/dspsr/code"
PRESTO_REPO="https://github.com/scottransom/presto.git"
SIGPROC_REPO="https://github.com/SixByNine/sigproc.git"
TEMPO_REPO="git://git.code.sf.net/p/tempo/tempo"
TEMPO2_REPO="https://bitbucket.org/psrsoft/tempo2.git"
JOBS="$(nproc)"
SKIP_PSRCHIVE=0
SKIP_DSPSR=0
SKIP_PRESTO=0
SKIP_PINT=0
SKIP_RFICLEAN=0
SKIP_SIGPROC=0
SKIP_PGPLOT=0
SKIP_TEMPO=0
SKIP_TEMPO2=0
SKIP_PSRDADA=0
UPDATE_SOURCES=0
CLEAN_BUILD=0
RECLONE_ON_DIVERGE=0
WITH_PSRCHIVE_PLOT=1
PGPLOT_DIR=""
DSPSR_BACKENDS="dada"

while (($#)); do
  case "$1" in
    --prefix)
      PREFIX="$2"
      shift 2
      ;;
    --psrhome)
      PSRHOME="$2"
      shift 2
      ;;
    --psrdada-src)
      PSRDADA_SRC="$2"
      shift 2
      ;;
    --psrdada-repo)
      PSRDADA_REPO="$2"
      shift 2
      ;;
    --psrchive-src)
      PSRCHIVE_SRC="$2"
      shift 2
      ;;
    --psrchive-repo)
      PSRCHIVE_REPO="$2"
      shift 2
      ;;
    --pgplot-src)
      PGPLOT_SRC="$2"
      shift 2
      ;;
    --pgplot-url)
      PGPLOT_URL="$2"
      shift 2
      ;;
    --dspsr-src)
      DSPSR_SRC="$2"
      shift 2
      ;;
    --dspsr-repo)
      DSPSR_REPO="$2"
      shift 2
      ;;
    --presto-src)
      PRESTO_SRC="$2"
      shift 2
      ;;
    --presto-repo)
      PRESTO_REPO="$2"
      shift 2
      ;;
    --presto-venv)
      PRESTO_VENV="$2"
      shift 2
      ;;
    --pint-src)
      PINT_SRC="$2"
      shift 2
      ;;
    --pint-repo)
      PINT_REPO="$2"
      shift 2
      ;;
    --pytools-venv)
      PYTOOLS_VENV="$2"
      shift 2
      ;;
    --rficlean-src)
      RFICLEAN_SRC="$2"
      shift 2
      ;;
    --rficlean-repo)
      RFICLEAN_REPO="$2"
      shift 2
      ;;
    --sigproc-src)
      SIGPROC_SRC="$2"
      shift 2
      ;;
    --sigproc-repo)
      SIGPROC_REPO="$2"
      shift 2
      ;;
    --tempo-src)
      TEMPO_SRC="$2"
      shift 2
      ;;
    --tempo-repo)
      TEMPO_REPO="$2"
      shift 2
      ;;
    --tempo2-src)
      TEMPO2_SRC="$2"
      shift 2
      ;;
    --tempo2-repo)
      TEMPO2_REPO="$2"
      shift 2
      ;;
    --skip-psrdada)
      SKIP_PSRDADA=1
      shift
      ;;
    --skip-pgplot)
      SKIP_PGPLOT=1
      shift
      ;;
    --skip-psrchive)
      SKIP_PSRCHIVE=1
      shift
      ;;
    --skip-dspsr)
      SKIP_DSPSR=1
      shift
      ;;
    --skip-presto)
      SKIP_PRESTO=1
      shift
      ;;
    --skip-pint)
      SKIP_PINT=1
      shift
      ;;
    --skip-rficlean)
      SKIP_RFICLEAN=1
      shift
      ;;
    --skip-sigproc)
      SKIP_SIGPROC=1
      shift
      ;;
    --skip-tempo)
      SKIP_TEMPO=1
      shift
      ;;
    --skip-tempo2)
      SKIP_TEMPO2=1
      shift
      ;;
    --update-sources)
      UPDATE_SOURCES=1
      shift
      ;;
    --clean)
      CLEAN_BUILD=1
      shift
      ;;
    --reclone-on-diverge)
      RECLONE_ON_DIVERGE=1
      shift
      ;;
    --with-psrchive-plot)
      WITH_PSRCHIVE_PLOT=1
      shift
      ;;
    --without-psrchive-plot)
      WITH_PSRCHIVE_PLOT=0
      shift
      ;;
    --pgplot-dir)
      PGPLOT_DIR="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --dspsr-backends)
      DSPSR_BACKENDS="$2"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
  esac
done

require_cmd() {
  local cmd="$1"
  if ! command -v "$cmd" >/dev/null 2>&1; then
    echo "Missing required command: $cmd" >&2
    exit 1
  fi
}

require_pkg_config_module() {
  local module="$1"
  local hint="$2"
  if ! pkg-config --exists "$module"; then
    echo "Missing required pkg-config module: $module" >&2
    echo "$hint" >&2
    exit 1
  fi
}

find_python_ge_39() {
  local candidate
  for candidate in python3.12 python3.11 python3.10 python3.9 python3; do
    if command -v "$candidate" >/dev/null 2>&1 && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      printf '%s\n' "$candidate"
      return 0
    fi
  done
  return 1
}

ensure_python_venv() {
  local venv_dir="$1"
  local host_python
  host_python="$(find_python_ge_39 || true)"
  if [[ -z "$host_python" ]]; then
    echo "Python >= 3.9 is required, but no suitable interpreter was found." >&2
    exit 1
  fi
  if "$host_python" -m venv --help >/dev/null 2>&1; then
    if [[ -x "$venv_dir/bin/python" ]] && ! "$venv_dir/bin/python" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 9) else 1)' >/dev/null 2>&1; then
      rm -rf "$venv_dir"
    fi
    "$host_python" -m venv "$venv_dir"
    "$venv_dir/bin/python" -m pip install --upgrade pip setuptools wheel >/dev/null
    printf '%s\n' "$venv_dir/bin/python"
    return 0
  fi
  printf '%s\n' "$host_python"
}

upsert_bashrc_env() {
  local bashrc="${HOME}/.bashrc"
  local begin="# >>> pulsar-stack >>>"
  local end="# <<< pulsar-stack <<<"
  local tmp
  tmp="$(mktemp)"
  if [[ -f "$bashrc" ]]; then
    awk -v begin="$begin" -v end="$end" '
      $0 == begin { skip=1; next }
      $0 == end { skip=0; next }
      !skip { print }
    ' "$bashrc" > "$tmp"
  fi
  {
    echo "$begin"
    echo "export PSRHOME=\"$PSRHOME\""
    echo "export PREFIX=\"$PREFIX\""
    echo "export PRESTO_VENV=\"${PRESTO_VENV:-$PREFIX/presto-venv}\""
    echo "export PYTOOLS_VENV=\"${PYTOOLS_VENV:-$PREFIX/python-tools-venv}\""
    echo "export PATH=\"\$PYTOOLS_VENV/bin:\$PRESTO_VENV/bin:$PREFIX/bin:\$PATH\""
    echo "export LD_LIBRARY_PATH=\"$PREFIX/lib:\${LD_LIBRARY_PATH:-}\""
    echo "export CPATH=\"$PREFIX/include:\${CPATH:-}\""
    echo "export LIBRARY_PATH=\"$PREFIX/lib:\${LIBRARY_PATH:-}\""
    echo "export PKG_CONFIG_PATH=\"$PREFIX/lib/pkgconfig:\${PKG_CONFIG_PATH:-}\""
    echo "export PGPLOT_DIR=\"${PGPLOT_DIR:-$PSRHOME/pgplot}\""
    echo "export PRESTO=\"${PRESTO_SRC:-$PSRHOME/presto}\""
    echo "export TEMPO=\"$PREFIX/tempo\""
    echo "export TEMPO2=\"$PREFIX/share/tempo2\""
    echo "$end"
    cat "$tmp"
  } > "${tmp}.new"
  mv "${tmp}.new" "$bashrc"
  rm -f "$tmp"
  echo "Updated $bashrc with pulsar stack environment"
}

have_prefix_psrdada() {
  [[ -x "$PREFIX/bin/dada_db" && ( -e "$PREFIX/lib/pkgconfig/psrdada.pc" || -e "$PREFIX/bin/psrdada.pc" ) ]]
}

have_prefix_pgplot() {
  [[ -d "$PGPLOT_DIR" && -e "$PGPLOT_DIR/libpgplot.a" && -e "$PGPLOT_DIR/libcpgplot.a" ]]
}

have_prefix_psrchive() {
  [[ -x "$PREFIX/bin/psredit" ]]
}

have_prefix_dspsr() {
  [[ -x "$PREFIX/bin/dspsr" ]]
}

have_prefix_presto() {
  [[ -x "$PREFIX/bin/prepfold" && -x "$PREFIX/bin/rfifind" ]] && compgen -G "$PREFIX/lib/libpresto.*" >/dev/null
}

have_prefix_sigproc() {
  [[ -x "$PREFIX/bin/filterbank" && -x "$PREFIX/bin/dedisperse" && -x "$PREFIX/bin/fold" ]]
}

have_prefix_tempo() {
  [[ -x "$PREFIX/bin/tempo" && -f "$PREFIX/tempo/tempo.cfg" && -f "$PREFIX/tempo/obsys.dat" ]]
}

have_prefix_tempo2() {
  [[ -x "$PREFIX/bin/tempo2" && -d "$PREFIX/share/tempo2" ]]
}

should_rebuild_installed() {
  [[ "$CLEAN_BUILD" -eq 1 ]]
}

verify_install() {
  local component="$1"
  local hint="$2"
  local ok=1
  case "$component" in
    PSRDADA)
      have_prefix_psrdada && ok=0
      ;;
    PSRCHIVE)
      have_prefix_psrchive && ok=0
      ;;
    DSPSR)
      have_prefix_dspsr && ok=0
      ;;
    PRESTO)
      have_prefix_presto && ok=0
      ;;
    SIGPROC)
      have_prefix_sigproc && ok=0
      ;;
    TEMPO)
      have_prefix_tempo && ok=0
      ;;
    TEMPO2)
      have_prefix_tempo2 && ok=0
      ;;
    *)
      echo "Unknown install verification target: $component" >&2
      exit 1
      ;;
  esac
  if [[ "$ok" -ne 0 ]]; then
    echo "$component install not detected under $PREFIX" >&2
    echo "$hint" >&2
    exit 1
  fi
}

check_tree() {
  local dir="$1"
  local desc="$2"
  if [[ ! -d "$dir/.git" && ! -f "$dir/configure.ac" && ! -f "$dir/bootstrap" && ! -f "$dir/autoconf.boot" ]]; then
    echo "Missing ${desc} source tree: $dir" >&2
    exit 1
  fi
}

run_autotools_build() {
  local dir="$1"
  local desc="$2"
  local build_cmd="$3"
  echo "==> Building $desc in $dir"
  (
    cd "$dir"
    /bin/bash -c "$build_cmd"
  )
}

get_psrdada_cflags() {
  if command -v psrdada_cflags >/dev/null 2>&1; then
    psrdada_cflags
  elif pkg-config --exists psrdada 2>/dev/null; then
    pkg-config --cflags psrdada
  fi
}

get_psrdada_libs() {
  if command -v psrdada_ldflags >/dev/null 2>&1; then
    psrdada_ldflags
  elif pkg-config --exists psrdada 2>/dev/null; then
    pkg-config --libs psrdada
  fi
}

get_psrdada_link_flags() {
  local flags=""
  if [[ -f "$PREFIX/lib/libpsrdada.so" || -f "$PREFIX/lib/libpsrdada.a" ]]; then
    flags="-L$PREFIX/lib -Wl,-rpath,$PREFIX/lib"
  fi
  if [[ -d "/usr/local/cuda/lib64" ]]; then
    flags="$flags -L/usr/local/cuda/lib64 -Wl,-rpath,/usr/local/cuda/lib64"
  fi
  if [[ -d "/usr/local/cuda-12.4/lib64" ]]; then
    flags="$flags -L/usr/local/cuda-12.4/lib64 -Wl,-rpath,/usr/local/cuda-12.4/lib64"
  fi
  printf '%s\n' "$flags"
}

warn_shadowed_psrdada() {
  if [[ -e "/usr/local/lib/libpsrdada.so" || -e "/usr/local/lib/libpsrdada.a" ]]; then
    echo "WARNING: Found PSRDADA under /usr/local/lib as well as the local stack under $PREFIX." >&2
    echo "WARNING: DSPSR must link against $PREFIX/lib/libpsrdada, not the stale /usr/local copy." >&2
  fi
}

update_tree() {
  local dir="$1"
  local desc="$2"
  if [[ "$UPDATE_SOURCES" -eq 0 ]]; then
    return 0
  fi
  echo "==> Updating $desc source tree"
  (
    cd "$dir"
    git fetch --all --tags
    if ! git pull --ff-only; then
      if [[ "$RECLONE_ON_DIVERGE" -eq 0 ]]; then
        echo "$desc source tree cannot be fast-forwarded." >&2
        echo "Rerun with --reclone-on-diverge to move the current tree aside and clone a fresh copy." >&2
        exit 1
      fi

      local remote_url
      local branch
      local backup_dir
      remote_url="$(git remote get-url origin)"
      branch="$(git rev-parse --abbrev-ref HEAD)"
      backup_dir="${dir}.backup.$(date +%Y%m%d_%H%M%S)"

      echo "==> $desc tree diverged; moving current tree to $backup_dir"
      cd ..
      mv "$(basename "$dir")" "$(basename "$backup_dir")"
      echo "==> Recloning $desc from $remote_url"
      git clone "$remote_url" "$(basename "$dir")"
      cd "$dir"
      if git show-ref --verify --quiet "refs/heads/$branch"; then
        git checkout "$branch"
      fi
    fi
    if [[ -f .gitmodules ]]; then
      git submodule update --init --recursive
    fi
  )
}

clone_tree() {
  local repo_url="$1"
  local dir="$2"
  local desc="$3"
  local parent_dir
  parent_dir="$(dirname "$dir")"
  mkdir -p "$parent_dir"
  echo "==> Cloning $desc from $repo_url into $dir"
  git clone "$repo_url" "$dir"
}

download_pgplot_source() {
  local url="$1"
  local dir="$2"
  local parent_dir
  local tmp_archive
  parent_dir="$(dirname "$dir")"
  mkdir -p "$parent_dir"
  tmp_archive="$(mktemp "${TMPDIR:-/tmp}/pgplot.XXXXXX.tar.gz")"
  echo "==> Downloading PGPLOT from $url"
  if command -v curl >/dev/null 2>&1; then
    curl -L "$url" -o "$tmp_archive"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$tmp_archive" "$url"
  else
    echo "Missing downloader: need curl or wget to fetch PGPLOT" >&2
    rm -f "$tmp_archive"
    exit 1
  fi
  rm -rf "$dir"
  mkdir -p "$dir"
  tar -xzf "$tmp_archive" -C "$dir" --strip-components=1
  rm -f "$tmp_archive"
}

download_file() {
  local url="$1"
  local output="$2"
  local parent_dir
  parent_dir="$(dirname "$output")"
  mkdir -p "$parent_dir"
  echo "==> Downloading $(basename "$output") from $url"
  if command -v curl >/dev/null 2>&1; then
    curl -L "$url" -o "$output"
  elif command -v wget >/dev/null 2>&1; then
    wget -O "$output" "$url"
  else
    echo "Missing downloader: need curl or wget to fetch $url" >&2
    exit 1
  fi
}

install_tempo_runtime() {
  local ephem_name
  local candidate
  mkdir -p "$PREFIX/tempo" "$PREFIX/tempo/tempo_ephem"
  rm -rf "$PREFIX/tempo/tempo_ephem"
  mkdir -p "$PREFIX/tempo/tempo_ephem"
  rm -rf "$PREFIX/tempo/clock"
  rm -rf "$PREFIX/tempo/tzpar"
  cp -R "$TEMPO_SRC/clock" "$PREFIX/tempo"
  cp "$TEMPO_SRC/obsys.dat" "$PREFIX/tempo/obsys.dat"
  cp "$TEMPO_SRC/tempo.cfg" "$PREFIX/tempo/tempo.cfg"
  cp "$TEMPO_SRC/tempo.hlp" "$PREFIX/tempo/tempo.hlp"
  if [[ -d "$TEMPO_SRC/tzpar" ]]; then
    cp -R "$TEMPO_SRC/tzpar" "$PREFIX/tempo/tzpar"
  else
    cp "$TEMPO_SRC/tzpar" "$PREFIX/tempo/tzpar"
  fi
  for ephem_name in DE200.1950.2050 DE405.1950.2050 TDB.1950.2050; do
    candidate=""
    for candidate in \
      "$TEMPO_SRC/${ephem_name}.gz" \
      "$TEMPO_SRC/$ephem_name" \
      "$TEMPO_SRC/ephem/${ephem_name}.gz" \
      "$TEMPO_SRC/ephem/$ephem_name"
    do
      if [[ -f "$candidate" ]]; then
        cp "$candidate" "$PREFIX/tempo/tempo_ephem/"
        break
      fi
    done
    if [[ ! -f "$PREFIX/tempo/tempo_ephem/${ephem_name}" && ! -f "$PREFIX/tempo/tempo_ephem/${ephem_name}.gz" ]]; then
      echo "Missing TEMPO ephemeris file: $ephem_name (looked in $TEMPO_SRC and $TEMPO_SRC/ephem)" >&2
      exit 1
    fi
  done
  perl -pi -e "s|/pulsar/psr/runtime|$PREFIX|g" "$PREFIX/tempo/tempo.cfg"
  perl -0pi -e 's{^CLKDIR\s+\S+}{CLKDIR         '"$PREFIX"'/tempo/clock/}m;
                 s{^PARDIR\s+\S+}{PARDIR         '"$PREFIX"'/tempo/tzpar/}m;
                 s{^EPHDIR\s+\S+}{EPHDIR         '"$PREFIX"'/tempo/tempo_ephem/}m;
                 s{^OBSYS\s+\S+}{OBSYS          '"$PREFIX"'/tempo/obsys.dat}m' \
    "$PREFIX/tempo/tempo.cfg"
  (
    cd "$PREFIX/tempo/tempo_ephem"
    for ephem_name in DE200.1950.2050 DE405.1950.2050 TDB.1950.2050; do
      if [[ -f "${ephem_name}.gz" ]]; then
        gunzip -f "${ephem_name}.gz"
      fi
    done
  )
}

patch_tempo_obsys() {
  local tempo_obsys="$1"
  if [[ -f "$tempo_obsys" ]]; then
    python3 - "$tempo_obsys" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text().splitlines()
remove_tokens = {"IAR1", "IAR2", "IAR1R", "IAR2R", "DSA3", "CLTC", " m  A1", " n  A1", " o  A2", " r  R1", " p  R1", " s  R2", " q  R2", " p  D3", " w  D3", " q  CL", " j  CL"}
filtered = []
local_names = {"IAR1", "IAR2", "IAR1R", "IAR2R", "DSA3", "CLTC"}
reserved_codes = {"m", "o", "r", "s", "p", "q", "-"}
seen_codes = set()
for line in lines:
    if any(token in line for token in remove_tokens):
        continue
    # IAR-first policy: remove any non-local observatory that occupies one of
    # the one-character TEMPO codes reserved for the local sites.
    if len(line) >= 71:
        name = line[50:69].strip()
        code = line[70:71]
        if code in reserved_codes and name not in local_names:
            continue
        # TEMPO rejects duplicate one-character site codes. Keep the first
        # surviving non-local entry for each code; local entries are appended
        # explicitly below after all existing local lines are removed.
        if code in seen_codes:
            continue
        seen_codes.add(code)
    filtered.append(line)

entries = [
    " -345159.0      580823.5          10.             IAR1                m  A1",
    " -345202.9      580823.4          10.             IAR2                o  A2",
    " -345159.0      580823.5          10.             IAR1R               r  R1",
    " -345202.9      580823.4          10.             IAR2R               s  R2",
    " -354633.1      692353.7         800.             DSA3                p  D3",
    " -381129.1      700858.4         800.             CLTC                q  CL",
]
filtered.extend(entries)
path.write_text("\n".join(filtered) + "\n")
PY
  fi
}

patch_tempo2_observatories() {
  local tempo2_observatories="$1"
  if [[ -f "$tempo2_observatories" ]]; then
    python3 - "$tempo2_observatories" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1])
lines = path.read_text().splitlines()
remove_tokens = {"IAR1", "IAR2", "IAR1R", "IAR2R", "DSA3", "CLTC", "iar1", "iar2", "iar1r", "iar2r", "dsa3", "cltc"}
filtered = []
for line in lines:
    if line.strip() == "# IAR":
        continue
    if any(token in line for token in remove_tokens):
        continue
    filtered.append(line)

entries = [
    "# IAR",
    " 2765357.08    -4449628.98      -3625726.47      IAR1                iar1",
    " 2765322.49    -4449569.52      -3625825.14      IAR2                iar2",
    " 2765357.08    -4449628.98      -3625726.47      IAR1R               iar1r",
    " 2765322.49    -4449569.52      -3625825.14      IAR2R               iar2r",
    " 1822902.736   -4849284.620     -3708078.704     DSA3                dsa3",
    " 1704386.809   -4721089.389     -3922212.645     CLTC                cltc",
]
filtered.extend(entries)
path.write_text("\n".join(filtered) + "\n")
PY
  fi
}

apply_local_sigproc_codes() {
  local src="$1"
  python3 - "$src" <<'PY'
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
candidates = [
    root / "src/aliases.c",
    root / "aliases.c",
]
path = next((candidate for candidate in candidates if candidate.exists()), None)
if path is None:
    raise SystemExit(0)

text = path.read_text()

tempo_cases = """case 19:
return 'm';
break;
case 20:
return 'o';
break;
case 21:
return 'r';
break;
case 22:
return 's';
break;
case 24:
return 'p';
break;
case 25:
return 'q';
break;
"""

telescope_cases = """case 19:
strcpy(string,"IAR1");
break;
case 20:
strcpy(string,"IAR2");
break;
case 21:
strcpy(string,"IAR1R");
break;
case 22:
strcpy(string,"IAR2R");
break;
case 24:
strcpy(string,"DSA3");
break;
case 25:
strcpy(string,"CLTC");
break;
"""

backend_cases = """case 23:
strcpy(string,"RTL_Filterbank");
break;
case 24:
strcpy(string,"IAR_ROACH_v1");
break;
case 25:
strcpy(string,"IAR_SNAP_v1");
break;
"""

def insert_before_default(func_name: str, snippet: str) -> None:
    global text
    if "IAR_ROACH_v1" in text and func_name == "backend_name":
        return
    if "IAR1" in text and func_name in {"tempo_site", "telescope_name"}:
        return
    pattern = re.compile(rf"(\b{re.escape(func_name)}\b\s*\([^)]*\)[\s\S]*?)(\n\s*default\s*:)", re.S)
    match = pattern.search(text)
    if not match:
        return
    prefix = match.group(1)
    default = match.group(2)
    text = text[:match.start()] + prefix + snippet + default + text[match.end():]

insert_before_default("tempo_site", tempo_cases)
insert_before_default("telescope_name", telescope_cases)
insert_before_default("backend_name", backend_cases)

path.write_text(text)

dmshift = root / "dmshift.c"
if dmshift.exists():
    dmshift_text = dmshift.read_text()
    if '#include <stdlib.h>' not in dmshift_text:
        dmshift_text = dmshift_text.replace('#include <stdio.h>\n', '#include <stdio.h>\n#include <stdlib.h>\n')
        dmshift.write_text(dmshift_text)

dosearch = root / "dosearch.f"
if dosearch.exists():
    dosearch_text = dosearch.read_text()
    dosearch_text = dosearch_text.replace("DB\\'s slow-but-simple harmonic summing routine",
                                          "DB''s slow-but-simple harmonic summing routine")
    dosearch.write_text(dosearch_text)

seekin = root / "seekin.f"
if seekin.exists():
    seekin_text = seekin.read_text()
    seekin_text = seekin_text.replace(
        "         write(*,1)'-submn   - mean subtraction (old method) to whiten spectrum'\n",
        "         write(*,1)'-submn   - mean subtraction (old method)'\n"
        "         write(*,1)'           to whiten spectrum'\n",
    )
    seekin_text = seekin_text.replace(
        "         write(*,1)'-n[nmax] - maximum number of single-pulse candidates per DM channel'\n",
        "         write(*,1)'-n[nmax] - maximum number of single-pulse'\n"
        "         write(*,1)'           candidates per DM channel'\n",
    )
    seekin_text = seekin_text.replace(
        "         write(*,1)'-w[smax] - number of times to smooth time series for single-pulse search'\n",
        "         write(*,1)'-w[smax] - number of times to smooth'\n"
        "         write(*,1)'           time series for single-pulse search'\n",
    )
    seekin.write_text(seekin_text)
PY
}

apply_local_presto_codes() {
  local src="$1"
  python3 - "$src" <<'PY'
from pathlib import Path
import sys

src = Path(sys.argv[1])

replacements = {
    "python/presto/sigproc.py": [
        (
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "ARECIBO 305m": 1,\n                 "Ooty": 2, "Nancay": 3, "Parkes": 4, "Jodrell": 5,\n                 "GBT": 6, "GMRT": 7, "Effelsberg": 8, "ATA": 9,\n                 "SRT": 10, "LOFAR": 11, "VLA": 12, "CHIME": 20,\n                 "FAST": 21, "MWA": 30, "MeerKAT": 64, "KAT-7": 65}\nids_to_telescope = dict(list(zip(list(telescope_ids.values()), list(telescope_ids.keys()))))\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2, "WAPP": 2, "AOFTM": 3,\n               "BCPM1": 4, "BPP": 4, "OOTY": 5, "SCAMP": 6,\n               "GBT Pulsar Spigot": 7, "SPIGOT": 7, "BG/P": 11,\n               "PDEV": 12, "CHIME+PSR": 20, "MWA-VCS": 30,\n               "MWAX-VCS": 31, "MWAX-RTB": 32, "KAT": 64, "KAT-DC2": 65}\nids_to_machine = dict(list(zip(list(machine_ids.values()), list(machine_ids.keys()))))\n""",
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "ARECIBO 305m": 1,\n                 "Ooty": 2, "Nancay": 3, "Parkes": 4, "Jodrell": 5,\n                 "GBT": 6, "GMRT": 7, "Effelsberg": 8, "ATA": 9,\n                 "SRT": 10, "LOFAR": 11, "VLA": 12,\n                 "A1": 19, "IAR1": 19,\n                 "A2": 20, "IAR2": 20,\n                 "R1": 21, "IAR1R": 21,\n                 "R2": 22, "IAR2R": 22,\n                 "D3": 24, "DSA3": 24,\n                 "CL": 25, "CLTC": 25,\n                 "MWA": 30, "MeerKAT": 64, "KAT-7": 65}\nids_to_telescope = dict(list(zip(list(telescope_ids.values()), list(telescope_ids.keys()))))\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2, "WAPP": 2, "AOFTM": 3,\n               "BCPM1": 4, "BPP": 4, "OOTY": 5, "SCAMP": 6,\n               "GBT Pulsar Spigot": 7, "SPIGOT": 7, "BG/P": 11,\n               "PDEV": 12, "RTL_Filterbank": 23,\n               "IAR_ROACH_v1": 24, "IAR_SNAP_v1": 25,\n               "MWA-VCS": 30, "MWAX-VCS": 31, "MWAX-RTB": 32,\n               "KAT": 64, "KAT-DC2": 65}\nids_to_machine = dict(list(zip(list(machine_ids.values()), list(machine_ids.keys()))))\n"""
        ),
    ],
    "bin/dat2tim.py": [
        (
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "Ooty": 2, "Nancay": 3,\n                 "Parkes": 4, "Jodrell": 5, "GBT": 6, "GMRT": 7,\n                 "Effelsberg": 8}\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2,"AOFTM": 3,\n               "BCPM1": 4, "OOTY": 5, "SCAMP": 6, \n               "GBT Pulsar Spigot": 7, "SPIGOT": 7}\n""",
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "Ooty": 2, "Nancay": 3,\n                 "Parkes": 4, "Jodrell": 5, "GBT": 6, "GMRT": 7,\n                 "Effelsberg": 8, "A1": 19, "IAR1": 19,\n                 "A2": 20, "IAR2": 20, "R1": 21, "IAR1R": 21,\n                 "R2": 22, "IAR2R": 22, "D3": 24, "DSA3": 24,\n                 "CL": 25, "CLTC": 25}\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2, "AOFTM": 3,\n               "BCPM1": 4, "OOTY": 5, "SCAMP": 6,\n               "GBT Pulsar Spigot": 7, "SPIGOT": 7,\n               "RTL_Filterbank": 23, "IAR_ROACH_v1": 24,\n               "IAR_SNAP_v1": 25}\n"""
        ),
    ],
    "bin/guppidrift2fil.py": [
        (
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "ARECIBO 305m": 1, "Ooty": 2, "Nancay": 3,\n                 "Parkes": 4, "Jodrell": 5, "GBT": 6, "GMRT": 7,\n                 "Effelsberg": 8, "ATA": 9, "UTR-2": 10, "LOFAR": 11}\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2, "WAPP": 2, "AOFTM": 3,\n               "BCPM1": 4, "OOTY": 5, "SCAMP": 6, "GBT Pulsar Spigot": 7, \n               "SPIGOT": 7, "BG/P": 11, "pdev": 11}\n""",
            """telescope_ids = {"Fake": 0, "Arecibo": 1, "ARECIBO 305m": 1, "Ooty": 2, "Nancay": 3,\n                 "Parkes": 4, "Jodrell": 5, "GBT": 6, "GMRT": 7,\n                 "Effelsberg": 8, "ATA": 9, "UTR-2": 10, "LOFAR": 11,\n                 "A1": 19, "IAR1": 19, "A2": 20, "IAR2": 20,\n                 "R1": 21, "IAR1R": 21, "R2": 22, "IAR2R": 22,\n                 "D3": 24, "DSA3": 24, "CL": 25, "CLTC": 25}\n\nmachine_ids = {"FAKE": 0, "PSPM": 1, "Wapp": 2, "WAPP": 2, "AOFTM": 3,\n               "BCPM1": 4, "OOTY": 5, "SCAMP": 6, "GBT Pulsar Spigot": 7,\n               "SPIGOT": 7, "BG/P": 11, "pdev": 11,\n               "RTL_Filterbank": 23, "IAR_ROACH_v1": 24,\n               "IAR_SNAP_v1": 25}\n"""
        ),
    ],
    "python/presto/polycos.py": [
        (
            """# Telescope name to TEMPO observatory code conversion\ntelescope_to_id = {"GBT": '1', \\\n                   "Arecibo":' 3', \\\n                   "VLA": '6', \\\n                   "Parkes": '7', \\\n                   "Jodrell": '8', \\\n                   "GB43m": 'a', \\\n                   "GB 140FT": 'a', \\\n                   "Nancay": 'f', \\\n                   "Effelsberg": 'g', \\\n                   "WSRT": 'i', \\\n                   "FAST": 'k', \\\n                   "GMRT": 'r', \\\n                   "CHIME": 'y', \\\n                   "Geocenter": '0', \\\n                   "Barycenter": '@'}\n\n# TEMPO observatory code to Telescope name conversion\nid_to_telescope = {'1': "GBT", \\\n                   '3': "Arecibo", \\\n                   '6': "VLA", \\\n                   '7': "Parkes", \\\n                   '8': "Jodrell", \\\n                   'a': "GB43m", \\\n                   'a': "GB 140FT", \\\n                   'f': "Nancay", \\\n                   'g': "Effelsberg", \\\n                   'i': "WSRT", \\\n                   'k': "FAST", \\\n                   'r': "GMRT", \\\n                   'y': "CHIME", \\\n                   '0': "Geocenter", \\\n                   '@': "Barycenter"}\n\n# Telescope name to track length (max hour angle) conversion\ntelescope_to_maxha = {"GBT": 12, \\\n                   "Arecibo": 3, \\\n                   "FAST": 5, \\\n                   "VLA": 6, \\\n                   "Parkes": 12, \\\n                   "Jodrell": 12, \\\n                   "GB43m": 12, \\\n                   "GB 140FT": 12, \\\n                   "Nancay": 4, \\\n                   "Effelsberg": 12, \\\n                   "WSRT": 12, \\\n                   "GMRT": 12, \\\n                   "CHIME": 1, \\\n                   "Geocenter": 12, \\\n                   "Barycenter": 12}\n""",
            """# Telescope name to TEMPO observatory code conversion\ntelescope_to_id = {"GBT": '1', \\\n                   "Arecibo":' 3', \\\n                   "VLA": '6', \\\n                   "Parkes": '7', \\\n                   "Jodrell": '8', \\\n                   "GB43m": 'a', \\\n                   "GB 140FT": 'a', \\\n                   "Nancay": 'f', \\\n                   "Effelsberg": 'g', \\\n                   "WSRT": 'i', \\\n                   "FAST": 'k', \\\n                   "CHIME": 'y', \\\n                   "A1": 'm', \\\n                   "IAR1": 'm', \\\n                   "A2": 'o', \\\n                   "IAR2": 'o', \\\n                   "R1": 'r', \\\n                   "IAR1R": 'r', \\\n                   "R2": 's', \\\n                   "IAR2R": 's', \\\n                   "D3": 'p', \\\n                   "DSA3": 'p', \\\n                   "CL": 'q', \\\n                   "CLTC": 'q', \\\n                   "Geocenter": '0', \\\n                   "Barycenter": '@'}\n\n# TEMPO observatory code to Telescope name conversion\nid_to_telescope = {'1': "GBT", \\\n                   '3': "Arecibo", \\\n                   '6': "VLA", \\\n                   '7': "Parkes", \\\n                   '8': "Jodrell", \\\n                   'a': "GB 140FT", \\\n                   'f': "Nancay", \\\n                   'g': "Effelsberg", \\\n                   'i': "WSRT", \\\n                   'k': "FAST", \\\n                   'y': "CHIME", \\\n                   'm': "IAR1", \\\n                   'o': "IAR2", \\\n                   'r': "IAR1R", \\\n                   's': "IAR2R", \\\n                   'p': "DSA3", \\\n                   'q': "CLTC", \\\n                   '0': "Geocenter", \\\n                   '@': "Barycenter"}\n\n# Telescope name to track length (max hour angle) conversion\ntelescope_to_maxha = {"GBT": 12, \\\n                   "Arecibo": 3, \\\n                   "FAST": 5, \\\n                   "VLA": 6, \\\n                   "Parkes": 12, \\\n                   "Jodrell": 12, \\\n                   "GB43m": 12, \\\n                   "GB 140FT": 12, \\\n                   "Nancay": 4, \\\n                   "Effelsberg": 12, \\\n                   "WSRT": 12, \\\n                   "CHIME": 1, \\\n                   "A1": 12, \\\n                   "IAR1": 12, \\\n                   "A2": 12, \\\n                   "IAR2": 12, \\\n                   "R1": 12, \\\n                   "IAR1R": 12, \\\n                   "R2": 12, \\\n                   "IAR2R": 12, \\\n                   "D3": 12, \\\n                   "DSA3": 12, \\\n                   "CL": 12, \\\n                   "CLTC": 12, \\\n                   "Geocenter": 12, \\\n                   "Barycenter": 12}\n"""
        ),
    ],
    "bin/get_TOAs.py": [
        (
            """scopes = {'GBT':'1',\n          'Arecibo':'3',\n          'Parkes':'7',\n          'GMRT': 'r',\n          'IRAM': 's',\n          'LWA1': 'x',\n          'LWA': 'x',\n          'MWA': 'u',\n          'VLA': 'c',\n          'FAST': 'k',\n          'MeerKAT': 'm',\n          'Geocenter': 'o'}\n\nscopes2 = {'GBT':'gbt',\n          'Arecibo':'ao',\n          'Parkes':'pks',\n          'GMRT': 'gmrt',\n          'LWA1': 'lwa1',\n          'LWA': 'lwa1',\n          'MWA': 'mwa',\n          'VLA': 'vla',\n          'FAST': 'fast',\n          'MeerKAT': 'mk',\n          'Geocenter': 'coe'}\n""",
            """scopes = {'GBT':'1',\n          'Arecibo':'3',\n          'Parkes':'7',\n          'A1': 'm',\n          'IAR1': 'm',\n          'A2': 'o',\n          'IAR2': 'o',\n          'R1': 'r',\n          'IAR1R': 'r',\n          'R2': 's',\n          'IAR2R': 's',\n          'D3': 'p',\n          'DSA3': 'p',\n          'CL': 'q',\n          'CLTC': 'q',\n          'LWA1': 'x',\n          'LWA': 'x',\n          'MWA': 'u',\n          'VLA': 'c',\n          'FAST': 'k',\n          'Geocenter': '0'}\n\nscopes2 = {'GBT':'gbt',\n          'Arecibo':'ao',\n          'Parkes':'pks',\n          'A1': 'a1',\n          'IAR1': 'a1',\n          'A2': 'a2',\n          'IAR2': 'a2',\n          'R1': 'r1',\n          'IAR1R': 'r1',\n          'R2': 'r2',\n          'IAR2R': 'r2',\n          'D3': 'd3',\n          'DSA3': 'd3',\n          'CL': 'cl',\n          'CLTC': 'cl',\n          'LWA1': 'lwa1',\n          'LWA': 'lwa1',\n          'MWA': 'mwa',\n          'VLA': 'vla',\n          'FAST': 'fast',\n          'MeerKAT': 'mk',\n          'Geocenter': 'coe'}\n"""
        ),
    ],
    "src/sigproc_fb.c": [
        (
            """    case 12:\n        strcpy(s->telescope, "VLA");\n        s->beam_FWHM = default_beam;\n        break;\n    case 20:  // May need to change....\n        strcpy(s->telescope, "CHIME");\n        s->beam_FWHM = 2.0 / 3600.0 * beam_halfwidth(s->fctr, 20.0);\n        break;\n    case 21:  // May need to change....\n        strcpy(s->telescope, "FAST");\n        s->beam_FWHM = 2.0 / 3600.0 * beam_halfwidth(s->fctr, 350.0);\n        break;\n    case 30:\n        strcpy(s->telescope, "MWA");\n        s->beam_FWHM = default_beam;\n        break;\n    case 64:\n        strcpy(s->telescope, "MeerKAT");\n        s->beam_FWHM = default_beam;\n        break;\n    case 65:\n        strcpy(s->telescope, "KAT-7");\n        s->beam_FWHM = default_beam;\n        break;\n""",
            """    case 12:\n        strcpy(s->telescope, "VLA");\n        s->beam_FWHM = default_beam;\n        break;\n    case 19:\n        strcpy(s->telescope, "IAR1");\n        s->beam_FWHM = default_beam;\n        break;\n    case 20:\n        strcpy(s->telescope, "IAR2");\n        s->beam_FWHM = default_beam;\n        break;\n    case 21:\n        strcpy(s->telescope, "IAR1R");\n        s->beam_FWHM = default_beam;\n        break;\n    case 22:\n        strcpy(s->telescope, "IAR2R");\n        s->beam_FWHM = default_beam;\n        break;\n    case 24:\n        strcpy(s->telescope, "DSA3");\n        s->beam_FWHM = default_beam;\n        break;\n    case 25:\n        strcpy(s->telescope, "CLTC");\n        s->beam_FWHM = default_beam;\n        break;\n    case 30:\n        strcpy(s->telescope, "MWA");\n        s->beam_FWHM = default_beam;\n        break;\n    case 64:\n        strcpy(s->telescope, "MeerKAT");\n        s->beam_FWHM = default_beam;\n        break;\n    case 65:\n        strcpy(s->telescope, "KAT-7");\n        s->beam_FWHM = default_beam;\n        break;\n"""
        ),
        (
            """    case 20:\n        strcpy(string, "CHIME+PSR");\n        break;\n    case 30:\n        strcpy(string, "MWA-VCS"); // Legacy MWA voltage capture system (retired Aug 2021)\n        break;\n""",
            """    case 20:\n        strcpy(string, "CHIME+PSR");\n        break;\n    case 23:\n        strcpy(string, "RTL_Filterbank");\n        break;\n    case 24:\n        strcpy(string, "IAR_ROACH_v1");\n        break;\n    case 25:\n        strcpy(string, "IAR_SNAP_v1");\n        break;\n    case 30:\n        strcpy(string, "MWA-VCS"); // Legacy MWA voltage capture system (retired Aug 2021)\n        break;\n"""
        ),
    ],
    "src/polycos.c": [
        (
            """    } else if (strcmp(idata->telescope, "ATA") == 0) {\n        scopechar = 's';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "LOFAR") == 0) {\n        scopechar = 't';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "WSRT") == 0) {\n""",
            """    } else if ((strcmp(idata->telescope, "IAR2R") == 0) ||\n               (strcmp(idata->telescope, "R2") == 0)) {\n        scopechar = 's';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "LOFAR") == 0) {\n        scopechar = 't';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "WSRT") == 0) {\n"""
        ),
        (
            """    } else if (strcmp(idata->telescope, "FAST") == 0) {\n        scopechar = 'k';\n        tracklen = 5;\n    } else if (strcmp(idata->telescope, "GMRT") == 0) {\n        scopechar = 'r';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "CHIME") == 0) {\n""",
            """    } else if (strcmp(idata->telescope, "FAST") == 0) {\n        scopechar = 'k';\n        tracklen = 5;\n    } else if ((strcmp(idata->telescope, "IAR1R") == 0) ||\n               (strcmp(idata->telescope, "R1") == 0)) {\n        scopechar = 'r';\n        tracklen = 12;\n    } else if ((strcmp(idata->telescope, "DSA3") == 0) ||\n               (strcmp(idata->telescope, "D3") == 0)) {\n        scopechar = 'p';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "CHIME") == 0) {\n"""
        ),
        (
            """    } else if (strcmp(idata->telescope, "MWA") == 0) {\n        scopechar = 'u';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "LWA") == 0) {\n        scopechar = 'x';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "SRT") == 0) {\n        scopechar = 'z';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "MeerKAT") == 0) {\n        scopechar = 'm';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "KAT-7") == 0) {\n        scopechar = 'k';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "Geocenter") == 0) {\n        scopechar = 'o';\n        tracklen = 12;\n    } else {                    /*  Barycenter */\n""",
            """    } else if (strcmp(idata->telescope, "MWA") == 0) {\n        scopechar = 'u';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "LWA") == 0) {\n        scopechar = 'x';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "SRT") == 0) {\n        scopechar = 'z';\n        tracklen = 12;\n    } else if ((strcmp(idata->telescope, "IAR1") == 0) ||\n               (strcmp(idata->telescope, "A1") == 0)) {\n        scopechar = 'm';\n        tracklen = 12;\n    } else if ((strcmp(idata->telescope, "IAR2") == 0) ||\n               (strcmp(idata->telescope, "A2") == 0)) {\n        scopechar = 'o';\n        tracklen = 12;\n    } else if ((strcmp(idata->telescope, "CLTC") == 0) ||\n               (strcmp(idata->telescope, "CL") == 0)) {\n        scopechar = 'q';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "KAT-7") == 0) {\n        scopechar = 'k';\n        tracklen = 12;\n    } else if (strcmp(idata->telescope, "Geocenter") == 0) {\n        scopechar = '0';\n        tracklen = 12;\n    } else {                    /*  Barycenter */\n"""
        ),
    ],
    "src/misc_utils.c": [
        (
            """    } else if (strcmp(scope, "ata") == 0) {\n        strcpy(obscode, "AT");\n        strcpy(outname, "ATA");\n""",
            """    } else if ((strcmp(scope, "iar1") == 0) || (strcmp(scope, "a1") == 0)) {\n        strcpy(obscode, "A1");\n        strcpy(outname, "IAR1");\n    } else if ((strcmp(scope, "iar2") == 0) || (strcmp(scope, "a2") == 0)) {\n        strcpy(obscode, "A2");\n        strcpy(outname, "IAR2");\n    } else if ((strcmp(scope, "iar1r") == 0) || (strcmp(scope, "r1") == 0)) {\n        strcpy(obscode, "R1");\n        strcpy(outname, "IAR1R");\n    } else if ((strcmp(scope, "iar2r") == 0) || (strcmp(scope, "r2") == 0)) {\n        strcpy(obscode, "R2");\n        strcpy(outname, "IAR2R");\n    } else if ((strcmp(scope, "dsa3") == 0) || (strcmp(scope, "d3") == 0)) {\n        strcpy(obscode, "D3");\n        strcpy(outname, "DSA3");\n    } else if ((strcmp(scope, "cltc") == 0) || (strcmp(scope, "cl") == 0)) {\n        strcpy(obscode, "CL");\n        strcpy(outname, "CLTC");\n    } else if (strcmp(scope, "ata") == 0) {\n        strcpy(obscode, "AT");\n        strcpy(outname, "ATA");\n"""
        ),
    ],
}

for relpath, pairs in replacements.items():
    path = src / relpath
    if not path.exists():
        continue
    text = path.read_text()
    updated = text
    for old, new in pairs:
        updated = updated.replace(old, new)
    if updated != text:
        path.write_text(updated)
PY
}

apply_local_dspsr_codes() {
  local src="$1"
  python3 - "$src" <<'PY'
from pathlib import Path
import sys

path = Path(sys.argv[1]) / "Kernel/Formats/sigproc/SigProcObservation.C"
if not path.exists():
    raise SystemExit(0)

text = path.read_text()
replacements = [
    (
        """    case 12:\n      return "VLA";\n    case 64:\n      return "MeerKAT";\n    default:\n      return "unknown";\n""",
        """    case 12:\n      return "VLA";\n    case 19:\n      return "IAR1";\n    case 20:\n      return "IAR2";\n    case 21:\n      return "IAR1R";\n    case 22:\n      return "IAR2R";\n    case 24:\n      return "DSA3";\n    case 25:\n      return "CLTC";\n    case 64:\n      return "MeerKAT";\n    default:\n      return "unknown";\n"""
    ),
    (
        """    else if (itoa == "SR") return 10;\n    else if (itoa == "LF") return 11;\n    else if (itoa == "VL") return 12;\n    else if (itoa == "MK") return 64;\n    else return 0;\n""",
        """    else if (itoa == "SR") return 10;\n    else if (itoa == "LF") return 11;\n    else if (itoa == "VL") return 12;\n    else if (itoa == "A1") return 19;\n    else if (itoa == "A2") return 20;\n    else if (itoa == "R1") return 21;\n    else if (itoa == "R2") return 22;\n    else if (itoa == "D3") return 24;\n    else if (itoa == "CL") return 25;\n    else if (itoa == "MK") return 64;\n    else return 0;\n"""
    ),
    (
        """    case 11:\n      return "COBALT";\n    default:\n      return "?????";\n""",
        """    case 11:\n      return "COBALT";\n    case 23:\n      return "RTL_Filterbank";\n    case 24:\n      return "IAR_ROACH_v1";\n    case 25:\n      return "IAR_SNAP_v1";\n    default:\n      return "?????";\n"""
    ),
]

updated = text
for old, new in replacements:
    updated = updated.replace(old, new)
if updated != text:
    path.write_text(updated)
PY
}

install_presto() {
  local src="$1"
  local host_python
  local venv_python
  host_python="$(find_python_ge_39 || true)"
  if [[ -z "$host_python" ]]; then
    echo "PRESTO Python package requires Python >= 3.9, but no suitable interpreter was found." >&2
    exit 1
  fi
  venv_python="$host_python"
  echo "==> Building PRESTO in $src"
  (
    cd "$src"
    if [[ "$CLEAN_BUILD" -eq 1 && -f Makefile ]]; then
      make clean >/dev/null 2>&1 || true
    fi
    if [[ "$CLEAN_BUILD" -eq 1 && -f src/Makefile ]]; then
      make -C src cleaner >/dev/null 2>&1 || true
    fi
    if [[ "$CLEAN_BUILD" -eq 1 && -d build && -f meson.build ]]; then
      rm -rf build
    fi

    mkdir -p "$PREFIX/bin" "$PREFIX/lib"

    if "$host_python" -m venv --help >/dev/null 2>&1; then
      venv_python="$(ensure_python_venv "$PRESTO_VENV")"
      "$venv_python" -m pip install --upgrade pip setuptools wheel >/dev/null
      "$venv_python" -m pip install --upgrade "numpy<2" meson meson-python ninja
    fi

    export PRESTO="$src"
    export PRESTO_VENV
    export PATH="$PRESTO_VENV/bin:$PREFIX/bin:$PATH"
    export LD_LIBRARY_PATH="$PREFIX/lib:${LD_LIBRARY_PATH:-}"
    export LIBRARY_PATH="$PREFIX/lib:${LIBRARY_PATH:-}"
    export LDFLAGS="${LDFLAGS:-} -lgfortran -lquadmath -lm"

    if [[ -f meson.build ]]; then
      meson setup build --prefix="$PREFIX" --bindir=bin --libdir=lib
      "$venv_python" check_meson_build.py
      meson compile -C build
      meson install -C build
      if [[ -f python/pyproject.toml ]]; then
        (
          cd python
          "$venv_python" -m pip install .
        )
      fi
    elif [[ -f Makefile ]]; then
      make -j"$JOBS"
    elif [[ -f src/Makefile ]]; then
      make -C src -j"$JOBS"
    else
      echo "PRESTO source tree has no recognized build entrypoint (Makefile, src/Makefile, or meson.build): $src" >&2
      exit 1
    fi

    if [[ -d bin ]]; then
      find bin -maxdepth 1 -type f -perm -u+x -exec cp -f {} "$PREFIX/bin/" \;
    fi
    if [[ -d src ]]; then
      find src -maxdepth 1 -type f \( -name prepfold -o -name rfifind -o -name accelsearch -o -name prepsubband -o -name prepdata -o -name realfft -o -name mpiprepsubband \) \
        -exec cp -f {} "$PREFIX/bin/" \;
    fi
  )
}

install_psrchive_python_bindings() {
  local src="$1"
  local venv_python
  local python_include
  local numpy_include
  local python_site
  local python_flags
  if [[ ! -d "$src/More/python" ]]; then
    echo "PSRCHIVE Python binding sources are missing: $src/More/python" >&2
    exit 1
  fi
  require_cmd swig
  venv_python="$(ensure_python_venv "$PRESTO_VENV")"
  "$venv_python" -m pip install --upgrade "numpy<2"
  python_include="$("$venv_python" - <<'PY'
import sysconfig
print(sysconfig.get_config_var("INCLUDEPY"))
PY
)"
  numpy_include="$("$venv_python" - <<'PY'
import numpy
print(numpy.get_include())
PY
)"
  python_site="$("$venv_python" - <<'PY'
import site
import sysconfig
paths = [p for p in site.getsitepackages() if p.endswith("site-packages")]
print(paths[0] if paths else sysconfig.get_paths()["purelib"])
PY
)"
  if [[ ! -f "$python_include/Python.h" ]]; then
    echo "Python development headers are missing for PSRCHIVE bindings: $python_include/Python.h" >&2
    echo "Install python3-dev first, then rerun the installer." >&2
    exit 1
  fi
  python_flags="-I$python_include -I$numpy_include"
  if [[ -n "${CPPFLAGS:-}" ]]; then
    python_flags="$python_flags ${CPPFLAGS}"
  fi
  echo "==> Building PSRCHIVE Python bindings in $src/More/python"
  (
    cd "$src/More/python"
    make clean >/dev/null 2>&1 || true
    make -j"$JOBS" \
      pythondir="$python_site" \
      CPPFLAGS="$python_flags" \
      SWIG_FLAGS="-c++ -Wall -python -I../../local_include -I../.."
    make install \
      pythondir="$python_site" \
      CPPFLAGS="$python_flags" \
      SWIG_FLAGS="-c++ -Wall -python -I../../local_include -I../.."
  )
  "$venv_python" -c "import psrchive" >/dev/null
}

apply_local_pint_codes() {
  local src="$1"
  python3 - "$src" <<'PY'
from pathlib import Path
import json
import sys

root = Path(sys.argv[1])
json_path = root / "src/pint/data/runtime/observatories.json"
legacy_path = root / "src/pint/observatory/observatories.py"

if json_path.exists():
    data = json.loads(json_path.read_text())
    entries = {
        "iar1": {
            "tempo_code": "m",
            "itoa_code": "A1",
            "aliases": ["A1"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [2765357.08, -4449628.98, -3625726.47],
            "fullname": "IAR Antenna 1",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
        "iar2": {
            "tempo_code": "o",
            "itoa_code": "A2",
            "aliases": ["A2"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [2765322.49, -4449569.52, -3625825.14],
            "fullname": "IAR Antenna 2",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
        "iar1r": {
            "tempo_code": "r",
            "itoa_code": "R1",
            "aliases": ["R1"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [2765357.08, -4449628.98, -3625726.47],
            "fullname": "IAR Antenna 1 with ROACH backend",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
        "iar2r": {
            "tempo_code": "s",
            "itoa_code": "R2",
            "aliases": ["R2"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [2765322.49, -4449569.52, -3625825.14],
            "fullname": "IAR Antenna 2 with ROACH backend",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
        "dsa3": {
            "tempo_code": "p",
            "itoa_code": "D3",
            "aliases": ["D3"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [1822902.736, -4849284.620, -3708078.704],
            "fullname": "DSA-3",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
        "cltc": {
            "tempo_code": "q",
            "itoa_code": "CL",
            "aliases": ["CL"],
            "clock_file": "",
            "clock_fmt": "tempo2",
            "itrf_xyz": [1704386.809, -4721089.389, -3922212.645],
            "fullname": "CLTC",
            "origin": "Local IAR observatory definition added by install_pulsar_stack.sh.",
        },
    }
    data.update(entries)
    json_path.write_text(json.dumps(data, indent=4) + "\n")
    raise SystemExit(0)

if legacy_path.exists():
    text = legacy_path.read_text()
    if "IAR1" in text and "IAR2R" in text and "CLTC" in text:
        raise SystemExit(0)

    marker = "observatories = ["
    if marker not in text:
        marker = "known_observatories = ["
    if marker not in text:
        raise SystemExit("Could not find legacy PINT observatory registry to patch")

    entries = """
    Observatory(
        "IAR1",
        aliases=["A1"],
        tempo_code="m",
        itoa_code="A1",
        itrf_xyz=[2765357.08, -4449628.98, -3625726.47],
    ),
    Observatory(
        "IAR2",
        aliases=["A2"],
        tempo_code="o",
        itoa_code="A2",
        itrf_xyz=[2765322.49, -4449569.52, -3625825.14],
    ),
    Observatory(
        "IAR1R",
        aliases=["R1"],
        tempo_code="r",
        itoa_code="R1",
        itrf_xyz=[2765357.08, -4449628.98, -3625726.47],
    ),
    Observatory(
        "IAR2R",
        aliases=["R2"],
        tempo_code="s",
        itoa_code="R2",
        itrf_xyz=[2765322.49, -4449569.52, -3625825.14],
    ),
    Observatory(
        "DSA3",
        aliases=["D3"],
        tempo_code="p",
        itoa_code="D3",
        itrf_xyz=[1822902.736, -4849284.620, -3708078.704],
    ),
    Observatory(
        "CLTC",
        aliases=["CL"],
        tempo_code="q",
        itoa_code="CL",
        itrf_xyz=[1704386.809, -4721089.389, -3922212.645],
    ),
"""
    text = text.replace(marker, marker + entries, 1)
    legacy_path.write_text(text)
    raise SystemExit(0)

raise SystemExit("Could not find a PINT observatory definition file to patch")
PY
}

install_pint() {
  local src="$1"
  local venv_python
  echo "==> Installing PINT from $src"
  if [[ ! -f "$src/pyproject.toml" && ! -f "$src/setup.py" ]]; then
    echo "PINT source tree has no Python packaging metadata (pyproject.toml or setup.py): $src" >&2
    exit 1
  fi
  venv_python="$(ensure_python_venv "$PYTOOLS_VENV")"
  (
    cd "$src"
    "$venv_python" -m pip install .
  )
}

apply_local_rficlean_fixes() {
  local src="$1"
  python3 - "$src" <<'PY'
from pathlib import Path
import sys

root = Path(sys.argv[1])
header = root / "include/header.h"
globals_c = root / "src/header_globals.c"
makefile = root / "Makefile"

if header.exists():
    original = """/* global variables describing the data */
char rawdatafile[80], source_name[80];
int machine_id, telescope_id, data_type, nchans, nbits, nifs, scan_number,
  barycentric,pulsarcentric; /* these two added Aug 20, 2004 DRL */
double tstart,mjdobs,tsamp,fch1,foff,refdm,az_start,za_start,src_raj,src_dej;
double gal_l,gal_b,header_tobs,raw_fch1,raw_foff;
int nbeams, ibeam;
/* added 20 December 2000  JMC */
double srcl,srcb;
double ast0, lst0;
long wapp_scan_number;
char project[8];
char culprits[24];
double analog_power[2];

/* added frequency table for use with non-contiguous data */
//double frequency_table[4096]; /* note limited number of channels */
double frequency_table[32768]; /* note limited number of channels */
//double frequency_table[16384]; /* note limited number of channels */
long int npuls; /* added for binary pulse profile format */
"""
    replacement = """/* global variables describing the data */
extern char rawdatafile[80], source_name[80];
extern int machine_id, telescope_id, data_type, nchans, nbits, nifs, scan_number,
  barycentric,pulsarcentric; /* these two added Aug 20, 2004 DRL */
extern double tstart,mjdobs,tsamp,fch1,foff,refdm,az_start,za_start,src_raj,src_dej;
extern double gal_l,gal_b,header_tobs,raw_fch1,raw_foff;
extern int nbeams, ibeam;
/* added 20 December 2000  JMC */
extern double srcl,srcb;
extern double ast0, lst0;
extern long wapp_scan_number;
extern char project[8];
extern char culprits[24];
extern double analog_power[2];

/* added frequency table for use with non-contiguous data */
//extern double frequency_table[4096]; /* note limited number of channels */
extern double frequency_table[32768]; /* note limited number of channels */
//extern double frequency_table[16384]; /* note limited number of channels */
extern long int npuls; /* added for binary pulse profile format */
"""
    text = header.read_text()
    if "extern char rawdatafile[80], source_name[80];" not in text:
        text = text.replace(original, replacement)
        header.write_text(text)

globals_text = """#include "header.h"

char rawdatafile[80], source_name[80];
int machine_id, telescope_id, data_type, nchans, nbits, nifs, scan_number,
  barycentric,pulsarcentric;
double tstart,mjdobs,tsamp,fch1,foff,refdm,az_start,za_start,src_raj,src_dej;
double gal_l,gal_b,header_tobs,raw_fch1,raw_foff;
int nbeams, ibeam;
double srcl,srcb;
double ast0, lst0;
long wapp_scan_number;
char project[8];
char culprits[24];
double analog_power[2];
double frequency_table[32768];
long int npuls;
"""
if not globals_c.exists():
    globals_c.write_text(globals_text)

if makefile.exists():
    text = makefile.read_text()
    if "header_globals.o" not in text:
        text = text.replace(
            "_OBJ = bcast_header.o  pack_unpack.o  rficlean.o  scaledata.o  strings_equal.o  cleanit.o  read_block.o  rficlean_data.o  send_stuff.o swap_bytes.o  nsamples.o  read_header.o sizeof_file.o plot_data.o",
            "_OBJ = bcast_header.o  pack_unpack.o  rficlean.o  scaledata.o  strings_equal.o  cleanit.o  read_block.o  rficlean_data.o  send_stuff.o swap_bytes.o  nsamples.o  read_header.o sizeof_file.o plot_data.o header_globals.o",
        )
        makefile.write_text(text)
PY
}

install_rficlean() {
  local src="$1"
  local rficlean_cflags
  local rficlean_libs
  echo "==> Installing rficlean from $src"
  if [[ ! -f "$src/Makefile" ]]; then
    echo "rficlean source tree has no Makefile: $src" >&2
    exit 1
  fi
  (
    cd "$src"
    if [[ "$CLEAN_BUILD" -eq 1 ]]; then
      make clean >/dev/null 2>&1 || true
    fi
    apply_local_rficlean_fixes "$src"
    mkdir -p "$PREFIX/bin"
    rficlean_cflags="-Iinclude -Wno-unused-result -O3 -fcommon"
    rficlean_libs="-L$PREFIX/lib -lfftw3 -lcpgplot -lpgplot -lX11 -lgfortran -lquadmath -lm"
    make MYBIN="$PREFIX/bin/" CFLAGS="$rficlean_cflags" LIBS="$rficlean_libs" -j"$JOBS"
    make MYBIN="$PREFIX/bin/" CFLAGS="$rficlean_cflags" LIBS="$rficlean_libs" install
  )
}

install_sigproc() {
  local src="$1"
  echo "==> Building SIGPROC in $src"
  (
    cd "$src"
    if [[ ! -x ./bootstrap ]]; then
      echo "SIGPROC source tree does not contain ./bootstrap: $src" >&2
      exit 1
    fi

    if [[ "$CLEAN_BUILD" -eq 1 ]]; then
      make distclean >/dev/null 2>&1 || make clean >/dev/null 2>&1 || true
    fi

    mkdir -p "$PREFIX/bin" "$PREFIX/lib" "$PREFIX/include"

    ./bootstrap
    if [[ ! -x ./configure ]]; then
      echo "SIGPROC bootstrap did not produce ./configure: $src" >&2
      exit 1
    fi
    env \
      CC="${CC:-gcc}" \
      CXX="${CXX:-g++}" \
      FC="${FC:-gfortran}" \
      F77="${F77:-gfortran}" \
      CPPFLAGS="-I$PREFIX/include ${CPPFLAGS:-}" \
      LDFLAGS="-L$PREFIX/lib ${LDFLAGS:-}" \
      FFLAGS="${FFLAGS:-} -ffixed-line-length-none -std=legacy" \
      ./configure --prefix="$PREFIX"
    if [[ -f src/Makefile ]]; then
      perl -0pi -e 's/^sigproc\.h: include\.csh\n\t\$\(src\)\/include\.csh\n/sigproc.h:\n\t@true\n/m' src/Makefile
    fi
    if [[ -d src ]]; then
      (
        cd src
        python3 - <<'PY'
from pathlib import Path

src = Path(".")
version_history = src / "version.history"
version = "unknown"
if version_history.exists():
    lines = [line.strip() for line in version_history.read_text().splitlines() if line.strip()]
    if len(lines) >= 2:
        version = lines[-2].split()[0]
    elif lines:
        version = lines[-1].split()[0]

decls = []
for path in sorted(src.glob("*.c")):
    for line in path.read_text(errors="ignore").splitlines():
        if "includefile" in line:
            decls.append(line.split("/*", 1)[0].rstrip() + ";")

out = [
    f"/* sigproc.h: Automatically generated include file for sigproc-{version} */",
    "#pragma once",
    "#ifdef __cplusplus",
    'extern "C" {',
    "#endif",
    '#include "polyco.h"',
    '#include "epn.h"',
    '#include "version.h"',
    "#include <stdio.h>",
]
out.extend(sorted(dict.fromkeys(decls)))
out.extend([
    "#ifdef __cplusplus",
    "}",
    "#endif",
    "",
])
(src / "sigproc.h").write_text("\n".join(out))
PY
      )
    fi
    make -j"$JOBS"
    make install
  )
}

build_pgplot() {
  local src="$1"
  local out="$2"
  local conf_name="gfortran_local"
  local x_inc=""
  local x_lib=""
  local token
  echo "==> Building PGPLOT in $src"
  (
    cd "$src"
    mkdir -p "$out"
    export PGPLOT_DIR="$src"
    if [[ "$CLEAN_BUILD" -eq 1 ]]; then
      rm -f *.o *.a pgxwin_server cpgdemo pgdemo
    fi
    if [[ ! -x ./makemake ]]; then
      echo "PGPLOT source tree does not contain ./makemake: $src" >&2
      exit 1
    fi
    cp -f drivers.list drivers.list.dist
    perl -0pi -e '
      s/^!\s*(PSDRIV\s+1\s+\/PS\s+.*)$/ $1/mg;
      s/^!\s*(PSDRIV\s+2\s+\/VPS\s+.*)$/ $1/mg;
      s/^!\s*(PSDRIV\s+3\s+\/CPS\s+.*)$/ $1/mg;
      s/^!\s*(PSDRIV\s+4\s+\/VCPS\s+.*)$/ $1/mg;
      s/^!\s*(XWDRIV\s+1\s+\/XWINDOW\s+.*)$/ $1/mg;
      s/^!\s*(XWDRIV\s+2\s+\/XSERVE\s+.*)$/ $1/mg;
    ' drivers.list
    if [[ ! -f "sys_linux/${conf_name}.conf" ]]; then
      cp sys_linux/g77_gcc.conf "sys_linux/${conf_name}.conf"
    fi
    perl -0pi -e 's/FCOMPL="g77"/FCOMPL="gfortran"/g' "sys_linux/${conf_name}.conf"
    if pkg-config --exists x11; then
      while read -r token; do
        case "$token" in
          -I*)
            if [[ -z "$x_inc" && -d "${token#-I}" ]]; then
              x_inc="${token#-I}"
            fi
            ;;
          -L*)
            if [[ -z "$x_lib" && -d "${token#-L}" ]]; then
              x_lib="${token#-L}"
            fi
            ;;
        esac
      done < <(pkg-config --cflags --libs x11 xt)
    fi
    if [[ -z "$x_inc" ]]; then
      for token in /usr/include/X11 /usr/X11R6/include /opt/X11/include; do
        if [[ -d "$token" ]]; then
          x_inc="$token"
          break
        fi
      done
    fi
    if [[ -z "$x_lib" ]]; then
      for token in /usr/lib/x86_64-linux-gnu /usr/lib64 /usr/lib /usr/X11R6/lib /opt/X11/lib; do
        if [[ -d "$token" ]]; then
          x_lib="$token"
          break
        fi
      done
    fi
    if [[ -d "$x_inc" ]]; then
      perl -0pi -e 's|XINCL="-I/usr/X11R6/include"|XINCL="-I'"$x_inc"'"|g' "sys_linux/${conf_name}.conf"
    fi
    if [[ -d "$x_lib" ]]; then
      perl -0pi -e 's|LIBS="-L/usr/X11R6/lib -lX11"|LIBS="-L'"$x_lib"' -lX11 -lXt"|g' "sys_linux/${conf_name}.conf"
    fi
    ./makemake "$src" linux "$conf_name"
    make -j"$JOBS" lib grfont.dat
    make libcpgplot.a cpgplot.h
    make pgxwin_server || true
    mkdir -p "$PREFIX/include" "$PREFIX/lib"
    cp -f cpgplot.h "$PREFIX/include/"
    cp -f libpgplot.a "$PREFIX/lib/"
    cp -f libcpgplot.a "$PREFIX/lib/"
    if [[ "$out" != "$src" ]]; then
      cp -f libpgplot.a "$out/" 2>/dev/null || true
      cp -f libcpgplot.a "$out/" 2>/dev/null || true
      cp -f cpgplot.h "$out/" 2>/dev/null || true
      cp -f grfont.dat "$out/" 2>/dev/null || true
      cp -f rgb.txt "$out/" 2>/dev/null || true
      cp -f pgplot.doc "$out/" 2>/dev/null || true
      cp -f pgxwin_server "$out/" 2>/dev/null || true
    fi
  )
}

clean_tree() {
  local dir="$1"
  local desc="$2"
  if [[ "$CLEAN_BUILD" -eq 0 ]]; then
    return 0
  fi
  echo "==> Cleaning $desc build tree"
  (
    cd "$dir"
    if [[ -f Makefile ]]; then
      make distclean >/dev/null 2>&1 || make clean >/dev/null 2>&1 || true
    fi
  )
}

require_cmd git
require_cmd make
require_cmd gcc
require_cmd g++
require_cmd autoconf
require_cmd automake
require_cmd pkg-config
require_cmd tar
if [[ "$SKIP_PRESTO" -eq 0 ]]; then
  require_cmd python3
fi

mkdir -p "$PSRHOME" "$PREFIX"
mkdir -p "$PREFIX/bin" "$PREFIX/lib" "$PREFIX/include"

if [[ -z "$PSRDADA_SRC" ]]; then
  PSRDADA_SRC="$PSRHOME/psrdada"
fi
if [[ -z "$PSRCHIVE_SRC" ]]; then
  PSRCHIVE_SRC="$PSRHOME/psrchive"
fi
if [[ -z "$PGPLOT_SRC" ]]; then
  PGPLOT_SRC="$PSRHOME/pgplot-src"
fi
if [[ -z "$DSPSR_SRC" ]]; then
  DSPSR_SRC="$PSRHOME/dspsr"
fi
if [[ -z "$PRESTO_SRC" ]]; then
  PRESTO_SRC="$PSRHOME/presto"
fi
if [[ -z "$PRESTO_VENV" ]]; then
  PRESTO_VENV="$PREFIX/presto-venv"
fi
if [[ -z "$PINT_SRC" ]]; then
  PINT_SRC="$PSRHOME/PINT"
fi
if [[ -z "$PYTOOLS_VENV" ]]; then
  PYTOOLS_VENV="$PREFIX/python-tools-venv"
fi
if [[ -z "$RFICLEAN_SRC" ]]; then
  RFICLEAN_SRC="$PSRHOME/rficlean"
fi
if [[ -z "$SIGPROC_SRC" ]]; then
  SIGPROC_SRC="$PSRHOME/sigproc"
fi
if [[ -z "$TEMPO_SRC" ]]; then
  TEMPO_SRC="$PSRHOME/tempo"
fi
if [[ -z "$TEMPO2_SRC" ]]; then
  TEMPO2_SRC="$PSRHOME/tempo2"
fi
if [[ -z "$PGPLOT_DIR" ]]; then
  PGPLOT_DIR="$PSRHOME/pgplot"
fi

PSRCHIVE_CONFIGURE_ARGS=(--prefix="$PREFIX")

export PSRHOME
export PATH="$PYTOOLS_VENV/bin:$PRESTO_VENV/bin:$PREFIX/bin:$PATH"
export LD_LIBRARY_PATH="$PREFIX/lib:${LD_LIBRARY_PATH:-}"
export CPATH="$PREFIX/include:${CPATH:-}"
export LIBRARY_PATH="$PREFIX/lib:${LIBRARY_PATH:-}"
export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig:${PKG_CONFIG_PATH:-}"
export PRESTO="$PRESTO_SRC"
export PRESTO_VENV
export PYTOOLS_VENV
export TEMPO="$PREFIX/tempo"
export TEMPO2="$PREFIX/share/tempo2"

upsert_bashrc_env

echo "PSRHOME       : $PSRHOME"
echo "PREFIX        : $PREFIX"
echo "PSRDADA SRC   : $PSRDADA_SRC"
echo "PSRDADA REPO  : $PSRDADA_REPO"
echo "PGPLOT SRC    : ${PGPLOT_SRC:-not set}"
echo "PGPLOT URL    : $PGPLOT_URL"
echo "PSRCHIVE SRC  : $PSRCHIVE_SRC"
echo "PSRCHIVE REPO : $PSRCHIVE_REPO"
echo "DSPSR SRC     : $DSPSR_SRC"
echo "DSPSR REPO    : $DSPSR_REPO"
echo "PRESTO SRC    : $PRESTO_SRC"
echo "PRESTO REPO   : $PRESTO_REPO"
echo "PRESTO VENV   : $PRESTO_VENV"
echo "PINT SRC      : $PINT_SRC"
echo "PINT REPO     : $PINT_REPO"
echo "PYTOOLS VENV  : $PYTOOLS_VENV"
echo "RFICLEAN SRC  : $RFICLEAN_SRC"
echo "RFICLEAN REPO : ${RFICLEAN_REPO:-not set}"
echo "SIGPROC SRC   : $SIGPROC_SRC"
echo "SIGPROC REPO  : $SIGPROC_REPO"
echo "TEMPO SRC     : $TEMPO_SRC"
echo "TEMPO REPO    : $TEMPO_REPO"
echo "TEMPO2 SRC    : $TEMPO2_SRC"
echo "TEMPO2 REPO   : $TEMPO2_REPO"
echo "PGPLOT DIR    : ${PGPLOT_DIR:-not set}"
echo "JOBS          : $JOBS"
echo "PATH prefix   : $PREFIX/bin"

if [[ "$SKIP_PSRDADA" -eq 0 ]]; then
  if have_prefix_psrdada && ! should_rebuild_installed; then
    echo "==> Using existing PSRDADA install under $PREFIX"
  else
    if [[ ! -d "$PSRDADA_SRC" ]]; then
      clone_tree "$PSRDADA_REPO" "$PSRDADA_SRC" "PSRDADA"
    fi
    check_tree "$PSRDADA_SRC" "PSRDADA"
    update_tree "$PSRDADA_SRC" "PSRDADA"
    clean_tree "$PSRDADA_SRC" "PSRDADA"
    run_autotools_build "$PSRDADA_SRC" "PSRDADA" \
      "./bootstrap && ./configure --prefix=\"$PREFIX\" && make -j\"$JOBS\" && make install"
    verify_install "PSRDADA" "Expected $PREFIX/bin/dada_db and either $PREFIX/lib/pkgconfig/psrdada.pc or $PREFIX/bin/psrdada.pc after install."
  fi
fi

if [[ "$WITH_PSRCHIVE_PLOT" -eq 1 && "$SKIP_PGPLOT" -eq 0 ]]; then
  if have_prefix_pgplot && ! should_rebuild_installed; then
    echo "==> Using existing PGPLOT install under $PGPLOT_DIR"
  else
    if [[ ! -d "$PGPLOT_SRC" ]]; then
      download_pgplot_source "$PGPLOT_URL" "$PGPLOT_SRC"
    fi
    build_pgplot "$PGPLOT_SRC" "$PGPLOT_DIR"
    if have_prefix_pgplot; then
      echo "==> PGPLOT install detected under $PGPLOT_DIR"
    else
      echo "PGPLOT build finished but install was not detected under $PGPLOT_DIR" >&2
      exit 1
    fi
  fi
fi

if [[ "$WITH_PSRCHIVE_PLOT" -eq 1 ]]; then
  if [[ ! -d "$PGPLOT_DIR" ]]; then
    echo "PSRCHIVE plotting requested, but PGPLOT_DIR does not exist after the PGPLOT step: $PGPLOT_DIR" >&2
    exit 1
  fi
  PSRCHIVE_CONFIGURE_ARGS+=(--with-pgplot-dir="$PGPLOT_DIR")
fi

if [[ "$SKIP_PSRCHIVE" -eq 0 ]]; then
  if have_prefix_psrchive && ! should_rebuild_installed; then
    echo "==> Using existing PSRCHIVE install under $PREFIX"
  else
    if [[ ! -d "$PSRCHIVE_SRC" ]]; then
      clone_tree "$PSRCHIVE_REPO" "$PSRCHIVE_SRC" "PSRCHIVE"
    fi
    check_tree "$PSRCHIVE_SRC" "PSRCHIVE"
    update_tree "$PSRCHIVE_SRC" "PSRCHIVE"
    clean_tree "$PSRCHIVE_SRC" "PSRCHIVE"
    if [[ "$WITH_PSRCHIVE_PLOT" -eq 1 ]]; then
      echo "==> PSRCHIVE plotting requested via PGPLOT at $PGPLOT_DIR"
    else
      echo "==> PSRCHIVE plotting not requested; build may omit viewer tools such as pav"
    fi
    run_autotools_build "$PSRCHIVE_SRC" "PSRCHIVE" \
      "./bootstrap && SWIG=\"$(command -v swig)\" ./configure --enable-shared ${PSRCHIVE_CONFIGURE_ARGS[*]} && make -j\"$JOBS\" && make install"
    verify_install "PSRCHIVE" "Expected $PREFIX/bin/psredit after install."
    if [[ "$WITH_PSRCHIVE_PLOT" -eq 1 ]]; then
      if [[ -x "$PREFIX/bin/pav" ]]; then
        echo "==> PSRCHIVE plotting tool detected: $PREFIX/bin/pav"
      else
        echo "WARNING: PSRCHIVE built, but plotting tool 'pav' was not found under $PREFIX/bin" >&2
        echo "WARNING: Check your PGPLOT installation in $PGPLOT_DIR and rerun with --clean if needed." >&2
      fi
    fi
  fi
  install_psrchive_python_bindings "$PSRCHIVE_SRC"
fi

if [[ "$SKIP_DSPSR" -eq 0 ]]; then
  verify_install "PSRCHIVE" "DSPSR bootstrap needs a working PSRCHIVE install in $PREFIX first."
  verify_install "PSRDADA" "DSPSR DADA backend needs a working PSRDADA install in $PREFIX first."
  warn_shadowed_psrdada
  if [[ -d "$DSPSR_SRC" ]]; then
    apply_local_dspsr_codes "$DSPSR_SRC"
  fi
  if have_prefix_dspsr && ! should_rebuild_installed; then
    echo "==> Using existing DSPSR install under $PREFIX"
  else
    if [[ ! -d "$DSPSR_SRC" ]]; then
      clone_tree "$DSPSR_REPO" "$DSPSR_SRC" "DSPSR"
    fi
    check_tree "$DSPSR_SRC" "DSPSR"
    update_tree "$DSPSR_SRC" "DSPSR"
    apply_local_dspsr_codes "$DSPSR_SRC"
    clean_tree "$DSPSR_SRC" "DSPSR"
    run_autotools_build "$DSPSR_SRC" "DSPSR" \
      "printf '%s\n' \"$DSPSR_BACKENDS\" > backends.list && ./bootstrap && CPPFLAGS=\"$(get_psrdada_cflags) \${CPPFLAGS:-}\" LDFLAGS=\"$(get_psrdada_link_flags) \${LDFLAGS:-}\" LIBS=\"$(get_psrdada_libs) \${LIBS:-}\" ./configure --prefix=\"$PREFIX\" && make -j\"$JOBS\" && make install"
    verify_install "DSPSR" "Expected $PREFIX/bin/dspsr after install."
  fi
fi

if [[ "$SKIP_PRESTO" -eq 0 ]]; then
  require_pkg_config_module "glib-2.0" "Install the GLib development package (for Debian/Ubuntu: libglib2.0-dev)."
  require_pkg_config_module "fftw3f" "Install the FFTW3 single-precision development package (for Debian/Ubuntu: libfftw3-dev)."
  require_pkg_config_module "gsl" "Install the GNU Scientific Library development package (for Debian/Ubuntu: libgsl-dev)."
  require_pkg_config_module "cfitsio" "Install the CFITSIO development package (for Debian/Ubuntu: libcfitsio-dev)."
  require_pkg_config_module "libpng" "Install the libpng development package (for Debian/Ubuntu: libpng-dev)."
  if [[ -d "$PRESTO_SRC" ]]; then
    apply_local_presto_codes "$PRESTO_SRC"
  fi
  if have_prefix_presto && ! should_rebuild_installed; then
    echo "==> Using existing PRESTO install under $PREFIX"
  else
    if [[ ! -d "$PRESTO_SRC" ]]; then
      clone_tree "$PRESTO_REPO" "$PRESTO_SRC" "PRESTO"
    fi
    check_tree "$PRESTO_SRC" "PRESTO"
    update_tree "$PRESTO_SRC" "PRESTO"
    apply_local_presto_codes "$PRESTO_SRC"
    clean_tree "$PRESTO_SRC" "PRESTO"
    install_presto "$PRESTO_SRC"
    verify_install "PRESTO" "Expected at least $PREFIX/bin/prepfold and $PREFIX/bin/rfifind after install."
  fi
fi

if [[ "$SKIP_PINT" -eq 0 ]]; then
  if [[ ! -d "$PINT_SRC" ]]; then
    clone_tree "$PINT_REPO" "$PINT_SRC" "PINT"
  fi
  if [[ -d "$PINT_SRC/.git" ]]; then
    update_tree "$PINT_SRC" "PINT"
  fi
  apply_local_pint_codes "$PINT_SRC"
  install_pint "$PINT_SRC"
fi

if [[ "$SKIP_RFICLEAN" -eq 0 ]]; then
  if [[ ! -d "$RFICLEAN_SRC" ]]; then
    clone_tree "$RFICLEAN_REPO" "$RFICLEAN_SRC" "rficlean"
  fi
  if [[ -d "$RFICLEAN_SRC/.git" ]]; then
    update_tree "$RFICLEAN_SRC" "rficlean"
  fi
  install_rficlean "$RFICLEAN_SRC"
fi

if [[ "$SKIP_SIGPROC" -eq 0 ]]; then
  if [[ -d "$SIGPROC_SRC" ]]; then
    apply_local_sigproc_codes "$SIGPROC_SRC"
  fi
  if have_prefix_sigproc && ! should_rebuild_installed; then
    echo "==> Using existing SIGPROC install under $PREFIX"
  else
    if [[ ! -d "$SIGPROC_SRC" ]]; then
      clone_tree "$SIGPROC_REPO" "$SIGPROC_SRC" "SIGPROC"
    fi
    if [[ ! -d "$SIGPROC_SRC/.git" ]]; then
      echo "SIGPROC source tree exists but is not a git checkout: $SIGPROC_SRC" >&2
      echo "Remove or rename it, then rerun so the script can clone $SIGPROC_REPO" >&2
      exit 1
    fi
    if [[ ! -f "$SIGPROC_SRC/src/aliases.c" && ! -f "$SIGPROC_SRC/aliases.c" ]]; then
      echo "SIGPROC source tree is missing aliases.c: $SIGPROC_SRC" >&2
      exit 1
    fi
    apply_local_sigproc_codes "$SIGPROC_SRC"
    clean_tree "$SIGPROC_SRC" "SIGPROC"
    install_sigproc "$SIGPROC_SRC"
    verify_install "SIGPROC" "Expected at least $PREFIX/bin/filterbank, $PREFIX/bin/dedisperse, and $PREFIX/bin/fold after install."
  fi
fi

if [[ "$SKIP_TEMPO" -eq 0 ]]; then
  if have_prefix_tempo && ! should_rebuild_installed; then
    echo "==> Using existing TEMPO install under $PREFIX"
  else
    if [[ ! -d "$TEMPO_SRC" ]]; then
      clone_tree "$TEMPO_REPO" "$TEMPO_SRC" "TEMPO"
    fi
    check_tree "$TEMPO_SRC" "TEMPO"
    update_tree "$TEMPO_SRC" "TEMPO"
    patch_tempo_obsys "$TEMPO_SRC/obsys.dat"
    clean_tree "$TEMPO_SRC" "TEMPO"
    run_autotools_build "$TEMPO_SRC" "TEMPO" \
      "autoreconf --install && ./configure --prefix=\"$PREFIX\" && make -j\"$JOBS\" && make install"
    install_tempo_runtime
    verify_install "TEMPO" "Expected $PREFIX/bin/tempo plus $PREFIX/tempo/tempo.cfg and $PREFIX/tempo/obsys.dat after install."
  fi
fi

if [[ "$SKIP_TEMPO2" -eq 0 ]]; then
  if have_prefix_tempo2 && ! should_rebuild_installed; then
    echo "==> Using existing TEMPO2 install under $PREFIX"
  else
    if [[ ! -d "$TEMPO2_SRC" ]]; then
      clone_tree "$TEMPO2_REPO" "$TEMPO2_SRC" "TEMPO2"
    fi
    check_tree "$TEMPO2_SRC" "TEMPO2"
    update_tree "$TEMPO2_SRC" "TEMPO2"
    patch_tempo2_observatories "$TEMPO2_SRC/T2runtime/observatory/observatories.dat"
    clean_tree "$TEMPO2_SRC" "TEMPO2"
    run_autotools_build "$TEMPO2_SRC" "TEMPO2" \
      "./bootstrap && ./configure --prefix=\"$PREFIX\" && make -j\"$JOBS\" && make install && make plugins && make plugins-install"
    if [[ -d "$TEMPO2_SRC/T2runtime" ]]; then
      mkdir -p "$PREFIX/share"
      rm -rf "$PREFIX/share/tempo2"
      cp -r "$TEMPO2_SRC/T2runtime" "$PREFIX/share/tempo2"
      echo "Installed TEMPO2 runtime to $PREFIX/share/tempo2"
    fi
    verify_install "TEMPO2" "Expected $PREFIX/bin/tempo2 and $PREFIX/share/tempo2 after install."
  fi
fi

cat <<EOF

Install complete.

Environment for this shell:
  export PSRHOME="$PSRHOME"
  export PREFIX="$PREFIX"
  export PRESTO_VENV="$PRESTO_VENV"
  export PYTOOLS_VENV="$PYTOOLS_VENV"
  export PATH="\$PYTOOLS_VENV/bin:\$PRESTO_VENV/bin:$PREFIX/bin:\$PATH"
  export PRESTO="$PRESTO_SRC"
  export LD_LIBRARY_PATH="$PREFIX/lib:\${LD_LIBRARY_PATH:-}"
  export CPATH="$PREFIX/include:\${CPATH:-}"
  export LIBRARY_PATH="$PREFIX/lib:\${LIBRARY_PATH:-}"
  export PKG_CONFIG_PATH="$PREFIX/lib/pkgconfig:\${PKG_CONFIG_PATH:-}"
  export TEMPO="$PREFIX/tempo"
  export TEMPO2="$PREFIX/share/tempo2"

Sanity checks:
  which psredit || true
  which dspsr || true
  which prepfold || true
  which tempo2 || true
  which psrdada_cflags || true
EOF
