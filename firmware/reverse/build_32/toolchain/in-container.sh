#!/usr/bin/env bash
# Run a command inside the Wind River gcc-3.4.4 i386 build container, with the repo
# bind-mounted at its real path and the powerpc-wrs-vxworks toolchain bin/ on PATH.
#
#   toolchain/in-container.sh ccppc --version
#   toolchain/in-container.sh make -C firmware/reverse/build_32/src verify-relink
#
# Files written land in the bind-mounted repo owned by the host user (--user).
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO="$(cd "$HERE/../../../.." && pwd)"          # toolchain -> build_32 -> reverse -> firmware -> repo
TC="$HERE/wr-gcc-3.4.4-ppc/x86-linux2"
IMAGE="${WR_BUILD_IMAGE:-wr-build:3.4.4}"

if [ ! -x "$TC/bin/ccppc" ]; then
  echo "error: toolchain not found at $TC/bin/ccppc" >&2
  echo "extract it first (see toolchain/README.md)" >&2
  exit 1
fi

# Rootless Docker maps container-root -> the host user, so files written into the
# bind-mounted repo are owned by us; a traditional (root) daemon needs --user to avoid
# root-owned files. Pick whichever keeps repo writes owned by the invoking user.
USER_ARGS=()
if ! docker info -f '{{.SecurityOptions}}' 2>/dev/null | grep -q 'name=rootless'; then
  USER_ARGS=(--user "$(id -u):$(id -g)")
fi

exec docker run --rm -i \
  -v "$REPO:$REPO" -w "${PWD}" \
  "${USER_ARGS[@]}" \
  -e "PATH=$TC/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin" \
  -e "HOME=/tmp" \
  "$IMAGE" "$@"
