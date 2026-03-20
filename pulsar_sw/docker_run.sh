#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IMAGE_TAG="pulsar-stack:latest"

usage() {
  cat <<EOF
Usage: docker_run.sh [options] [-- <command>...]

Run the pulsar Docker image with useful bind mounts and host UID/GID mapping.

Default mounts:
  - current working directory -> /data
  - host home directory       -> /host_home

Default working directory inside container:
  - /data

Options:
  --image <name>      Docker image tag (default: $DEFAULT_IMAGE_TAG)
  --no-home           Do not mount $HOME to /host_home
  --no-pwd            Do not mount $PWD to /data
  --workdir <dir>     Working directory inside container (default: /data)
  --root              Run as root instead of host UID:GID
  --help              Show this help

Examples:
  ./docker_run.sh
  ./docker_run.sh -- bash
  ./docker_run.sh -- python -c "import pint; print(pint.__file__)"
EOF
}

IMAGE_TAG="$DEFAULT_IMAGE_TAG"
MOUNT_HOME=1
MOUNT_PWD=1
WORKDIR="/data"
RUN_AS_ROOT=0

while (($#)); do
  case "$1" in
    --image)
      IMAGE_TAG="$2"
      shift 2
      ;;
    --no-home)
      MOUNT_HOME=0
      shift
      ;;
    --no-pwd)
      MOUNT_PWD=0
      shift
      ;;
    --workdir)
      WORKDIR="$2"
      shift 2
      ;;
    --root)
      RUN_AS_ROOT=1
      shift
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    --)
      shift
      break
      ;;
    *)
      break
      ;;
  esac
done

if ! command -v docker >/dev/null 2>&1; then
  echo "Missing required command: docker" >&2
  exit 1
fi

docker_args=(
  run
  --rm
  -it
  -w "$WORKDIR"
  -e "PSRHOME=/opt/pulsar"
  -e "PREFIX=/opt/pulsar/install"
  -e "PRESTO_VENV=/opt/pulsar/install/presto-venv"
  -e "PYTOOLS_VENV=/opt/pulsar/install/python-tools-venv"
  -e "PGPLOT_DIR=/opt/pulsar/pgplot"
  -e "PRESTO=/opt/pulsar/presto"
  -e "TEMPO=/opt/pulsar/install/tempo"
  -e "TEMPO2=/opt/pulsar/install/share/tempo2"
  -e "HOST_HOME=/host_home"
  -e "PATH=/opt/pulsar/install/python-tools-venv/bin:/opt/pulsar/install/presto-venv/bin:/opt/pulsar/install/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
  -e "LD_LIBRARY_PATH=/opt/pulsar/install/lib"
  -e "CPATH=/opt/pulsar/install/include"
  -e "LIBRARY_PATH=/opt/pulsar/install/lib"
  -e "PKG_CONFIG_PATH=/opt/pulsar/install/lib/pkgconfig"
)

if [[ "$RUN_AS_ROOT" -eq 0 ]]; then
  docker_args+=(--user "$(id -u):$(id -g)")
fi

if [[ "$MOUNT_PWD" -eq 1 ]]; then
  docker_args+=(-v "$PWD:/data")
fi

if [[ "$MOUNT_HOME" -eq 1 ]]; then
  docker_args+=(-v "$HOME:/host_home")
  docker_args+=(-e "HOME=/tmp/pulsar-home")
  docker_args+=(-e "XDG_CACHE_HOME=/tmp/pulsar-home/.cache")
  docker_args+=(-e "XDG_CONFIG_HOME=/tmp/pulsar-home/.config")
elif [[ "$RUN_AS_ROOT" -eq 0 ]]; then
  docker_args+=(-e "HOME=/tmp/pulsar-home")
  docker_args+=(-e "XDG_CACHE_HOME=/tmp/pulsar-home/.cache")
  docker_args+=(-e "XDG_CONFIG_HOME=/tmp/pulsar-home/.config")
fi

docker_args+=("$IMAGE_TAG")

if (($#)); then
  docker_args+=("$@")
else
  docker_args+=("/bin/bash" "--noprofile" "--norc")
fi

docker "${docker_args[@]}"
