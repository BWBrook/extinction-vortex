# Live-request accounting for Stage 1b submissions (design 9h), sourced by s1b_submit.sh and the dispatchers; needs PBS
# (the PBS bin directory) and ME (the PBS user). Written for bash 4.2.
live_cpus() {      # CPUs of ME's queued, running and held jobs and subjobs; array parents excluded
  "$PBS/qstat" -t -u "$ME" | awk -v me="$ME" '$2 == me && $1 !~ /\[\]/ && $10 ~ /^[QRHWTSE]$/ {n += $7} END {print n + 0}'
}
unlisted() {       # accepted jobs in RUN's submission journals that ME's live listing omits and PBS does not show finished
  local run=$1 listing ended id num out
  listing=$("$PBS/qstat" -t -u "$ME" | awk '{print $1}')
  ended=$(cat "$run"/submit_*/submit_journal.tsv 2>/dev/null | awk '$1 == "terminal" {print $3}')
  for id in $(cat "$run"/submit_*/submit_journal.tsv 2>/dev/null | awk '$1 == "accepted" {print $4}' | sort -u); do
    num=${id%%[.[]*}
    if grep -q -e "^$num\\." -e "^$num\\[" <<< "$listing"; then continue; fi
    if grep -qxF "$id" <<< "$ended"; then continue; fi
    if out=$("$PBS/qstat" -x -f "$id" 2>/dev/null) && grep -q 'job_state = F' <<< "$out"; then continue; fi
    echo "$id"
  done
}
wait_listed() {    # until every job accepted in RUN's journals is listed or finished; fail closed after LIST_TRIES checks
  local run=$1 u i
  for i in $(seq 1 "${LIST_TRIES:-12}"); do
    u=$(unlisted "$run" | tr '\n' ' ')
    if [ -z "$u" ]; then return 0; fi
    echo "accepted jobs not yet listed: ${u% } (check $i)"; sleep "${LIST_SECS:-10}"
  done
  echo "accepted jobs still not listed: ${u% }; nothing more submitted (rerun once PBS lists them)"; exit 1
}
