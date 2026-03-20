#!/usr/bin/env bash
set -euo pipefail

DEFAULT_IMAGE_TAG="pulsar-stack:latest"

usage() {
  cat <<EOF
Usage: docker_install.sh [options]

Build a Docker image that installs the full pulsar stack inside the container
using install_pulsar_stack.sh.

Options:
  --image <name>      Docker image tag (default: $DEFAULT_IMAGE_TAG)
  --dockerfile <path> Dockerfile path (default: Dockerfile.pulsar)
  --jobs <n>          Build jobs forwarded into the image build (default: 4)
  --no-cache          Build without Docker cache
  --help              Show this help

Examples:
  ./docker_install.sh
  ./docker_install.sh --image pulsar-stack:dev --jobs 8
EOF
}

IMAGE_TAG="$DEFAULT_IMAGE_TAG"
DOCKERFILE="Dockerfile.pulsar"
JOBS="4"
NO_CACHE=0

while (($#)); do
  case "$1" in
    --image)
      IMAGE_TAG="$2"
      shift 2
      ;;
    --dockerfile)
      DOCKERFILE="$2"
      shift 2
      ;;
    --jobs)
      JOBS="$2"
      shift 2
      ;;
    --no-cache)
      NO_CACHE=1
      shift
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

if ! command -v docker >/dev/null 2>&1; then
  echo "Missing required command: docker" >&2
  exit 1
fi

build_args=(
  build
  -f "$DOCKERFILE"
  -t "$IMAGE_TAG"
  --build-arg "JOBS=$JOBS"
  .
)

if [[ "$NO_CACHE" -eq 1 ]]; then
  build_args=(build --no-cache -f "$DOCKERFILE" -t "$IMAGE_TAG" --build-arg "JOBS=$JOBS" .)
fi

docker "${build_args[@]}"

cat <<EOF

Docker image built:
  $IMAGE_TAG

Run it with:
  docker run --rm -it -v "\$PWD:/data" $IMAGE_TAG
EOF
