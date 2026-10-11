#!/usr/bin/env bash
# Agent-side TPAC kunanyi transport for the vortex validation, run on the Mac mini (where the
# TPAC credential env file lives; it is sourced into the environment, never printed). Barry
# opens the 5-minute Jumpbox window; each call below is a new authenticated connection.
#   tpac.sh run '<remote bash command>'          command on the kunanyi login node
#   tpac.sh push_from_deep DEEP_PATH KUNANYI_PATH  scp run on deep-server, through the jumpbox
#   tpac.sh pull_to_deep KUNANYI_PATH DEEP_PATH    the reverse
# The deep-server transfers follow dSDM goal 052: a local Expect answers the password prompts
# through a deep-server PTY; no credential is copied to deep-server or the cluster.
set -euo pipefail
NECTAR=${NECTAR:-$HOME/work/nectar}
export KUNANYI_CONNECT_TIMEOUT=${KUNANYI_CONNECT_TIMEOUT:-45}
export KUNANYI_EXPECT_TIMEOUT=${KUNANYI_EXPECT_TIMEOUT:-900}
mode=$1; shift
case "$mode" in
  run)
    cd "$NECTAR"
    source scripts/lib/common.sh; source scripts/lib/kunanyi.sh
    tpac_transport_setup
    tpac_expect_ssh "$1"
    ;;
  push_from_deep|pull_to_deep)
    set -a; source "${TPAC_SECRET_ENV:-$HOME/.config/tpac/kunanyi.env}"; set +a
    proxy="ProxyCommand=ssh -o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no -W %h:%p bwbrook@jumpbox.tpac.org.au"
    opts="-o StrictHostKeyChecking=accept-new -o PreferredAuthentications=password -o PubkeyAuthentication=no"
    if [ "$mode" = push_from_deep ]; then src=$1; dst="bwbrook@kunanyi:$2"; else src="bwbrook@kunanyi:$1"; dst=$2; fi
    export TPAC_SCP_CMD="scp $opts -o '$proxy' $src $dst"
    expect <<'EXP'
set timeout 1800
spawn ssh -tt -o BatchMode=yes deep-server $env(TPAC_SCP_CMD)
expect {
  -re "(?i)password:" {send -- "$env(TPAC_PASSWORD)\r"; exp_continue}
  timeout {exit 124}
  eof {catch wait result; exit [lindex $result 3]}
}
EXP
    ;;
  *) echo "usage: tpac.sh run CMD | push_from_deep SRC DST | pull_to_deep SRC DST" >&2; exit 2 ;;
esac
