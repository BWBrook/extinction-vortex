R=/u/bwbrook/vortex/run1/s1b/run2
echo "== $(TZ=Australia/Hobart date '+%F %T %Z') duplicate-claim census (read-only)"
ls $R/claimed > /tmp/claimed.$$; ls $R/queue > /tmp/queue.$$
echo "claims $(wc -l < /tmp/claimed.$$)  queued $(wc -l < /tmp/queue.$$)"
sed 's/^W[12]_[0-9]*_//; s/@.*//' /tmp/claimed.$$ | sort | uniq -c | awk '$1 > 1 {n++; c += $1} END {print "ranges with >1 claim:", n + 0, " claims on them:", c + 0}'
sed 's/^W[12]_[0-9]*_//; s/@.*//' /tmp/claimed.$$ | sort | uniq -c | sort -rn | head -5
sed 's/^W[12]_[0-9]*_//' /tmp/queue.$$ | sort > /tmp/qr.$$; sed 's/^W[12]_[0-9]*_//; s/@.*//' /tmp/claimed.$$ | sort -u > /tmp/cr.$$
echo "ranges both queued and claimed: $(comm -12 /tmp/qr.$$ /tmp/cr.$$ | wc -l)"; echo "queue names repeated: $(uniq -d /tmp/qr.$$ | wc -l)"
echo "by wave, claims: W1 $(grep -c '^W1_' /tmp/claimed.$$) W2 $(grep -c '^W2_' /tmp/claimed.$$)"
for w in W1 W2; do sed -n "s/^${w}_[0-9]*_//p" /tmp/claimed.$$ | sed 's/@.*//' | sort | uniq -c | awk -v w=$w '$1 > 1 {n++} END {print w, "ranges with >1 claim:", n + 0}'; done
rm -f /tmp/claimed.$$ /tmp/queue.$$ /tmp/qr.$$ /tmp/cr.$$; echo DUPS_DONE
