"""Scrub a receipt for the public repository, in place: drop SSH transport chatter, and replace cluster node names,
host names, the PBS server suffix, IP addresses and home paths with placeholders. Job IDs, digests and counts are kept.
Usage: scrub_receipt.py FILE [FILE ...]"""
import re, sys

DROP = re.compile(r"^(spawn ssh|spawn scp|\S+@\S+'s password:|\*\* |Warning: Permanently added|Connection closed by)")
SUBS = [
    (re.compile(r"/u/bwbrook/vortex/run1"), "$VB"),
    (re.compile(r"/u/bwbrook"), "~hpc"),
    (re.compile(r"/home/bwbrook"), "~"),
    (re.compile(r"/Users/bwbrook"), "~"),
    (re.compile(r"/data/fable/vortex"), "<deep>/vortex"),
    (re.compile(r"\.kunanyi-ohpc(@kunanyi-ohpc)?"), ""),
    (re.compile(r"\bkunanyi-ohpc\b"), "<server>"),
    (re.compile(r"\b[\w.-]*\.tpac\.org\.au\b"), "<host>"),
    (re.compile(r"\bkunanyi-\d+\b"), "<login>"),
    (re.compile(r"\bn\d{3}(\.kunanyi)?\b"), "<node>"),
    (re.compile(r"\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b"), "<addr>"),
]


def scrub(text):
    out = []
    for line in text.splitlines(keepends=True):
        if DROP.match(line.lstrip()):
            continue
        for pat, rep in SUBS:
            line = pat.sub(rep, line)
        out.append(line)
    return "".join(out)


if __name__ == "__main__":
    for f in sys.argv[1:]:
        s = open(f).read()
        open(f, "w").write(scrub(s))
