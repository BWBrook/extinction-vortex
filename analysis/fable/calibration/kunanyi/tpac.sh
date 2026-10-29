#!/usr/bin/env bash
# Agent-side TPAC kunanyi transport for the vortex validation, run on wsl, which reaches TPAC directly over the UTAS VPN
# (nectar docs/workflows/cross-machine-access.md, 29 October 2026; the Macs no longer reach deep). Nectar's helpers source
# the TPAC credential env file into the environment, never printing it. Barry opens the 5-minute Jumpbox window; each
# call below is a new authenticated connection. Files for deep go through wsl, which reaches deep directly.
#   tpac.sh run '<remote bash command>'      command on the kunanyi login node
#   tpac.sh push LOCAL_PATH KUNANYI_PATH      scp from wsl to kunanyi
#   tpac.sh pull KUNANYI_PATH LOCAL_PATH      scp from kunanyi to wsl
set -euo pipefail
NECTAR=${NECTAR:-$HOME/work/nectar}
export KUNANYI_SSH_ALIAS=${KUNANYI_SSH_ALIAS:-kunanyi}
export KUNANYI_CONNECT_TIMEOUT=${KUNANYI_CONNECT_TIMEOUT:-45}
timeout=${KUNANYI_EXPECT_TIMEOUT:-900}
mode=$1; shift
case "$mode" in
  run) args=("$1") ;;
  push) args=("$(realpath "$1")" "$KUNANYI_SSH_ALIAS:$2") ;;
  pull) args=("$KUNANYI_SSH_ALIAS:$1" "$(realpath -m "$2")") ;;
  *) echo "usage: tpac.sh run CMD | push LOCAL KUNANYI_PATH | pull KUNANYI_PATH LOCAL" >&2; exit 2 ;;
esac
cd "$NECTAR"
source scripts/lib/common.sh; source scripts/lib/kunanyi.sh
tpac_transport_setup; tpac_set_expect_timeout "$timeout"
if [ "$mode" = run ]; then tpac_expect_ssh "${args[0]}"; else tpac_expect_scp "${args[0]}" "${args[1]}"; fi
