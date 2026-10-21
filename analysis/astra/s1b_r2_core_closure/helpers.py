"""Independent closure replays for repaired Stage 1b core and node.

P3 functions/classes/constants are loaded unchanged via AST, without scientific
imports. P2 storage and run_setting functions are likewise loaded unchanged.
All filesystem state belongs to a temporary fixture. A logical clock prevents
real minutes of waiting; time advances only through explicit sleeps or stated
timeout fixtures. Unmocked sampling is forbidden.
"""
import ast
import contextlib
from datetime import datetime
import errno
import hashlib
import io
import json
import math
import os
from pathlib import Path
import random
import shutil
import subprocess
import sys
import tempfile
import time
import types
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
SRC = ROOT / 'analysis/fable/calibration/v2_dev'
P2, P3 = SRC / 'p2_stage1a.py', SRC / 'p3_stage1b.py'


class Clock:
    def __init__(self):
        self.now = 1000.
    def time(self):
        return self.now
    def sleep(self, secs):
        assert secs >= 0
        self.now += secs
    def process_time(self):
        return self.now / 1000.


def forbidden(*args, **kwargs):
    raise AssertionError('Unmocked scientific sampler is forbidden in this audit')


def modules():
    clock = Clock()
    p2 = types.ModuleType('p2_storage_audit')
    p2.__dict__.update(hashlib=hashlib, json=json, os=os, tempfile=tempfile,
                       time=clock, CKPT_SECS=60., EMPTY_SHA=hashlib.sha256(b'').hexdigest())
    names = {'sha', 'atomic_json', 'journal_prefix', 'replace_bytes', 'run_setting'}
    for node in ast.parse(P2.read_text()).body:
        if ((isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and
              t.id in ('COUNTERS', 'PARAMS', 'HIT_KEYS') for t in node.targets)) or
                (isinstance(node, ast.FunctionDef) and node.name in names)):
            exec(compile(ast.Module(body=[node], type_ignores=[]), str(P2), 'exec'), p2.__dict__)
    p2.one_batch = forbidden
    p2.runtime = lambda: {'audit': 'synthetic AST functions; no numerical runtime qualification'}
    p = types.ModuleType('p3_actual_functions')
    p.__dict__.update(__file__=str(P3), p2=p2, errno=errno, hashlib=hashlib, json=json,
                      math=math, os=os, random=random, shutil=shutil, subprocess=subprocess,
                      sys=sys, tempfile=tempfile, time=clock)
    nodes = [n for n in ast.parse(P3.read_text()).body
             if isinstance(n, (ast.Assign, ast.FunctionDef, ast.ClassDef))]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(P3), 'exec'), p.__dict__)
    p.K, p.BATCH = 5, 10
    return p, p2, clock


def make(tmp, name, p):
    d = tmp / name; run = d / 'run'; sd = run / 'sets/s00007'
    for path in ('queue', 'claimed', 'sets/s00007/ranges', 'lib', 'workers/dead'):
        (run / path).mkdir(parents=True, exist_ok=True)
    st = {'index': 7, 'pop': 'synthetic', 'outer': 'toy/0', 'n': 30,
          'E': {'n': 30, 'k': 1, 'r': 1}, 'rate': 10 / 3600,
          'cap_batches': 20, 'prior_hpb': 1., 'wave': 'W1', 'dir': 's00007',
          'library': 'primary', 'stream_tag': 2, 'pilot': None}
    b = {'settings': [st], 'metric_sha256': 'synthetic-metric',
         'runner_sha256': 'synthetic-runner', 'min_shard_cpu_h': 0.,
         'target_wall_h': 24., 'max_inflight': 1, 'overshoot': 1.}
    sp, mp = d / 'settings.json', d / 'metric.json'
    sp.write_text(json.dumps(b))
    mp.write_text(json.dumps({'outers': {'synthetic|toy/0': {'recorded': [4, 3, 0]}},
                             'pops': {'synthetic': {'keep': [], 'mad': []}}}))
    with p.held(str(sd), 'fixture-seed'):
        p.plan(st, str(sd), str(run), b)
    return d, run, sd, st, b, sp, mp


def fake_batch(p2, hits=5):
    def fake(st, mp, bi, B, des):
        x = {k: 0 for k in p2.COUNTERS}
        x.update(proposals=B, poisson_accept=B, theta_accept=B, paths=B,
                 selected_SA=hits, hits=hits, hits_lo=hits, hits_hi=hits)
        x['hit_records'] = [dict(batch=bi, proposal_in_batch=j, boundary=False,
                                 theta={k: .5 for k in p2.PARAMS}, recorded=[4, 3, 0])
                            for j in range(hits)]
        return x
    return fake


def proxy_os(**changes):
    values = {k: getattr(os, k) for k in dir(os)}
    values.update(changes)
    return types.SimpleNamespace(**values)
