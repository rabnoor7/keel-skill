#!/usr/bin/env python3
"""Regression selftest for keel's docs.py — run: python3 scripts/selftest.py

Locks the precision fixes for the two supersession detectors (keel doctrine: every fixed bug becomes a
permanent assertion). Both once fired on mere co-occurrence of a supersede-ish word + an ADR number on a
line (or, worse, spanning newlines), so normal prose like "override files … ADR 14" or "supersedes the
too_big idea; refines 0009" falsely retired live decisions — a gate that cries wolf. Fixtures below
reproduce those exact shapes and assert the detectors stay quiet on them while still catching real ones.

Isolated: builds a throwaway project dir, chdirs into it, then imports docs.py fresh (ROOT = getcwd())."""
import os, sys, tempfile, importlib.util

DOCS_PY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs.py')

DECISIONS = {
    # num: (body) — none self-marked "superseded" unless noted, so the detector's own guard doesn't hide bugs
    '0003': '# 0003 — thing three\nStatus: accepted\n',
    '0004': '# 0004 — thing four\nStatus: accepted\n',
    '0005': '# 0005 — thing five\nStatus: accepted\n',
    '0006': '# 0006 — thing six\nStatus: accepted\n',
    '0009': '# 0009 — classification\nStatus: accepted (revises the SKU reading of 0005)\n',
    '0010': '# 0010 — rubric\nStatus: accepted (supersedes the "too_big" idea; refines 0009)\n',  # 'refines 0009'
    '0013': '# 0013 — ig phase 2\nStatus: accepted\n',
    '0015': '# 0015 — ig embed\n**Status:** Accepted. Supersedes the instagrapi approach of ADR 0013 for scale.\n',
}
MEMORY = (
    'this note supersedes ADR 6 entirely.\n'                       # TP  (CONTRA_A: verb->ADR)   -> flag 6
    'ADR 3 is now superseded; framework removed.\n'               # TP  (CONTRA_B: ADR->dead)   -> flag 3
    '+ reviews JSON + override files. see ADR 4 for schema.\n'    # FP  ("override" noun)       -> quiet on 4
    'PHASE 1 = my job, do NOT web search — see ADR 5.\n'          # FP  ("do NOT" directive)    -> quiet on 5
)

EXPECT_CONTRA = {3, 6}          # not 4, not 5
EXPECT_SUSPECT = {'0013'}       # 0015 truly supersedes 0013; 0009 must NOT be flagged ("refines", bare number)


def build(root):
    os.makedirs(os.path.join(root, 'docs', 'decisions'))
    os.makedirs(os.path.join(root, 'docs', 'journal'))
    os.makedirs(os.path.join(root, 'memory'))
    for num, body in DECISIONS.items():
        with open(os.path.join(root, 'docs', 'decisions', f'{num}-x.md'), 'w') as fh:
            fh.write(body)
    with open(os.path.join(root, 'memory', 'notes.md'), 'w') as fh:
        fh.write(MEMORY)


def main():
    root = tempfile.mkdtemp(prefix='keel-selftest-')
    build(root)
    os.chdir(root)                                    # docs.py binds ROOT = os.getcwd() at import
    spec = importlib.util.spec_from_file_location('keel_docs', DOCS_PY)
    docs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(docs)

    fails = []
    contra = {n for (_tier, _rel, n, _line) in docs._contradictions()}
    if contra != EXPECT_CONTRA:
        fails.append(f'contradictions: got {sorted(contra)}, expected {sorted(EXPECT_CONTRA)}')

    suspect = {s.split('-')[0] for s in docs._suspect_decisions()}
    if suspect != EXPECT_SUSPECT:
        fails.append(f'suspect: got {sorted(suspect)}, expected {sorted(EXPECT_SUSPECT)}')

    # _next_adr date-draft immunity (the "2027 bug"): a date-named journal draft in .keel/pending/
    # once parsed as ADR 2026, so the next ADR landed as 2027-*.md. Fixed; locked here forever.
    os.makedirs(os.path.join(root, '.keel', 'pending'), exist_ok=True)
    with open(os.path.join(root, '.keel', 'pending', '2026-07-14-a-journal-draft.md'), 'w') as fh:
        fh.write('# a journal draft\n')
    nxt = docs._next_adr()
    if nxt != 16:  # highest real ADR in fixtures is 0015
        fails.append(f'_next_adr: got {nxt}, expected 16 (date-named draft must not poison numbering)')

    # the two convo-gate bugs, locked forever:
    # (a) a DECISIONS.md log is honored even when folder ADRs exist (recognition must not flip off)
    with open(os.path.join(root, 'docs', 'DECISIONS.md'), 'w') as fh:
        fh.write('# Decision Log\n\n(prose only — no numbered headings, so counts stay untouched)\n')
    if not (docs._dec_file() or '').endswith('DECISIONS.md'):
        fails.append('_dec_file: DECISIONS.md not honored while folder ADRs exist (recognition flipped off)')
    # (b) a DRAFTED decision appends its log pointer at landing (was silently skipped)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        docs._emit_record('decision', '0017-drafted-pointer-test.md', '# 0017 — drafted pointer test\n',
                          docs.DEC, True, 'drafted pointer test', {'n': 17})
        docs.cmd_hydrate(object())
    logtext = open(os.path.join(root, 'docs', 'DECISIONS.md')).read()
    if '> ADR 0017' not in logtext:
        fails.append('hydrate: drafted decision landed without appending its DECISIONS.md pointer')

    # every registered command family stays registered (guards against parser-wiring regressions)
    import io, contextlib
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf), contextlib.redirect_stderr(buf):
        try:
            sys.argv = ['docs.py', '--help']; docs.main()
        except SystemExit:
            pass
    helptext = buf.getvalue()
    for cmdname in ('rehydrate', 'layout', 'feedback', 'run', 'sink', 'stance', 'escalate', 'ask', 'discuss', 'status'):
        if cmdname not in helptext:
            fails.append(f'command "{cmdname}" missing from --help (parser wiring regressed)')

    # outcome decomposition: dormant with no roadmap; parses north-star + checkpoints when present
    if docs._roadmap() is not None:
        fails.append('_roadmap() must be None with no docs/roadmap.md (feature not dormant → breaks non-adopters)')
    os.makedirs(os.path.join(root, 'docs'), exist_ok=True)
    open(os.path.join(root, 'docs', 'roadmap.md'), 'w').write(
        '# Roadmap\n\n## North star\nbuild my brand\n\n## Checkpoints\n1. [reached] niche\n   - micro-niche chosen\n2. [active] audience\n')
    rm = docs._roadmap()
    if not rm or rm.get('north_star') != 'build my brand' or len(rm.get('checkpoints', [])) != 2:
        fails.append(f'_roadmap parse: got {rm} (expected north_star + 2 checkpoints)')
    elif [c['status'] for c in rm['checkpoints']] != ['reached', 'active']:
        fails.append('_roadmap: checkpoint statuses mis-parsed')

    # T1 · Discussion Mode locks — teeth at the BUILD moment only, advisory at rehydrate, per-thread exit.
    import types
    def _rc(fn, **kw):
        buf2 = io.StringIO()
        try:
            with contextlib.redirect_stdout(buf2), contextlib.redirect_stderr(buf2):
                fn(types.SimpleNamespace(**kw))
            return 0, buf2.getvalue()
        except SystemExit as e:
            return (e.code if isinstance(e.code, int) else 1), buf2.getvalue()
    _c = dict(content=None, from_file=None, approved=False, window=None, by=None, echo=None)
    _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'plan', 'approved': True,
                                            'by': 'selftest', 'echo': 'go ahead'})
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc != 0:
        fails.append(f'discuss: contract check must pass with no open thread (rc={rc}: {out.strip()[-100:]})')
    _rc(docs.cmd_discuss, action='open', thread='shape the access layer', id=None, choice=None, to_decision=None)
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc == 0 or 'DISCUSSION OPEN' not in out:
        fails.append('discuss: an open thread must BLOCK contract check (build-moment teeth)')
    # rehydrate must SURFACE the thread but stay advisory for it (rc not asserted here — this fixture
    # holds intentional contradictions that legitimately make rehydrate blocking on their own)
    rc, out = _rc(docs.cmd_rehydrate, full=False)
    if 'DISCUSSION MODE' not in out:
        fails.append('discuss: rehydrate must surface open threads')
    if 'DISCUSSION' in ''.join(x for x in out.splitlines() if x.startswith('[B')):
        fails.append('discuss: open threads must never be a rehydrate BLOCKING item (advisory only)')
    rc, _ = _rc(docs.cmd_discuss, action='close', id=1, choice='FastAPI', to_decision=None, thread=None)
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc != 0:
        fails.append('discuss: closing the last open thread must release the build gate')
    rc, _ = _rc(docs.cmd_discuss, action='close', id=1, choice=None, to_decision=None, thread=None)
    if rc == 0:
        fails.append('discuss: re-closing a settled thread must refuse (settled is settled)')

    # R2 unit 1 · echo-field approval floor (locked forever): an unattributed approval must refuse
    _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'echo-floor plan'})
    rc, out = _rc(docs.cmd_contract, action='approve', **_c)
    if rc == 0 or '--echo' not in out:
        fails.append('attribution: bare approve (no --by/--echo) must refuse and name the flags')
    rc, out = _rc(docs.cmd_contract, action='approve', **{**_c, 'by': 'user', 'echo': '   '})
    if rc == 0 or 'empty' not in out:
        fails.append('attribution: whitespace echo must refuse AND say the echo is empty (blind-UX fix)')
    rc, _ = _rc(docs.cmd_contract, action='approve', **{**_c, 'by': 'user', 'echo': 'yes build it'})
    if rc != 0:
        fails.append('attribution: approve with --by + --echo must succeed')
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc != 0 or 'approved by user (self-reported): "yes build it"' not in out or '✅ approved + fresh' not in out:
        fails.append('attribution: check must show approved-banner (never "signed") + approved-by + echo')
    rc, out = _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'side door', 'approved': True})
    if rc == 0 or '--echo' not in out:
        fails.append('attribution: set --approved without --by/--echo must refuse (side door)')
    import json as _cj
    _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'legacy shape'})
    _cj.dump({'plan': 'legacy', 'hash': 'x', 'ts': docs.time.time() - 7200, 'approved': True},
             open(os.path.join('.keel', 'contract.json'), 'w'))
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc == 0 or 'fresh=False' not in out:
        fails.append('attribution: legacy fielded-less contract must expire cleanly, not crash')

    # Unit 1.5 · concurrency-safe discuss store (locked forever)
    _d = dict(id=None, thread=None, choice=None, to_decision=None, as_writer=None, writer=None)
    rc, out = _rc(docs.cmd_discuss, action='open', **{**_d, 'thread': 'cross-writer thread', 'as_writer': 'alice'})
    _xid = int(out.split('#')[1].split(' ')[0])
    rc, out = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': _xid, 'as_writer': 'bob'})
    if rc == 0 or 'alice' not in out or '--writer' not in out:
        fails.append('concurrency: closing another writer\'s thread must refuse and name them + the override')
    # honesty lock (blind-UX 1.6.0): a writer label is a self-reported hint, never proof — the refusal must
    # never borrow permission/ownership vocabulary, or readers infer an identity check that does not exist
    if 'self-reported' not in out or 'not a permission check' not in out:
        fails.append('honesty: cross-writer refusal must state the label is self-reported and NOT a permission check')
    rc, _ = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': _xid, 'as_writer': 'bob', 'writer': 'alice'})
    if rc != 0:
        fails.append('concurrency: deliberate cross-writer close (--writer named) must succeed')
    rc, out = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': _xid, 'as_writer': 'bob', 'writer': 'alice'})
    if rc == 0 or 'already closed by "bob" (self-reported at close)' not in out:
        fails.append('concurrency: re-close must refuse naming WHO closed it (the incident forensics)')
    # the close-attributor must never be labelled "writer" — that word means the OPENER everywhere else
    if 'writer' in out.split('already closed')[-1]:
        fails.append('honesty: already-closed line must not call the closer a "writer" (opener/closer collision)')
    with open(os.path.join('.keel', 'discuss.jsonl'), 'a') as _fh:
        _fh.write(_cj.dumps({'id': 97, 'thread': 'legacy row no writer', 'status': 'open', 'ts': 0}) + '\n')
        _fh.write(_cj.dumps({'id': 98, 'thread': 'legacy row no writer 2', 'status': 'open', 'ts': 0}) + '\n')
        _fh.write(_cj.dumps({'kind': 'reconciliation-note', 'note': 'tolerated invisibly'}) + '\n')
    if 97 not in [r['id'] for r in docs._discuss_open()]:
        fails.append('concurrency: legacy writer-less rows must stay visible/open (forever-compat)')
    rc, _ = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': 97, 'as_writer': 'anyone'})
    if rc != 0:
        fails.append('concurrency: legacy writer-less rows must close without --writer (no gate on absent data)')
    # absent identity NEVER gates, even when the caller names a --writer: the guard keys on RECORDED identity
    # existing, not on it matching (without this the writer-less path passes by coincidence, not by design)
    rc, _ = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': 98, 'as_writer': 'anyone', 'writer': 'ghost'})
    if rc != 0:
        fails.append('concurrency: writer-less legacy rows must never gate on absent identity, even with --writer named')
    import subprocess as _sp, sys as _sys
    _dp = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'docs.py')
    _before = {r['id'] for r in docs._discuss_rows()}
    _procs = [_sp.Popen([_sys.executable, '-c',
                         'import subprocess,sys\n'
                         + 'for i in range(6): subprocess.run([sys.executable, %r, "discuss", "open", "--thread", '
                           '"storm-%s-"+str(i), "--as", "W%s"], capture_output=True)' % (_dp, w, w)])
              for w in ('a', 'b')]
    for _pp in _procs:
        _pp.wait()
    _after = [r['id'] for r in docs._discuss_rows()]
    if len(_after) != len(set(_after)) or len(set(_after) - _before) != 12:
        fails.append(f'concurrency: two-writer storm must yield 12 unique new ids, zero lost/duplicated '
                     f'(got {len(set(_after) - _before)} new, {len(_after) - len(set(_after))} dup)')

    # 1.6.1 locks: pid-fallback labels never gate (battery-caught cry-wolf); explicit labels still do
    rc, out = _rc(docs.cmd_discuss, action='open', **{**_d, 'thread': 'pid noise thread'})
    _pid_id = int(out.split('#')[1].split(' ')[0])
    rc, out = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': _pid_id, 'choice': 'done'})
    if rc != 0:
        fails.append('1.6.1: same-session close across pid-fallback labels must NOT gate (cry-wolf fix)')
    for _r9 in docs._discuss_rows():  # storm threads are pid-labeled: closing them exercises the fix x12
        if _r9.get('status') == 'open':
            rc, out = _rc(docs.cmd_discuss, action='close', **{**_d, 'id': _r9['id'], 'choice': 'cleanup',
                                                               'writer': _r9.get('writer')})
            if rc != 0:
                fails.append(f'1.6.1: pid-labeled thread #{_r9["id"]} refused a same-session close ({out[-80:]})')
    rc, out = _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'long echo plan'})
    rc, out = _rc(docs.cmd_contract, action='approve', **{**_c, 'by': 'user',
                                                          'echo': 'x' * 95})
    rc, out = _rc(docs.cmd_contract, action='check', **_c)
    if rc != 0 or '…' not in out:
        fails.append(f'1.6.1: clipped approval echo must end with an ellipsis, never cut bare (rc={rc})')

    # T2 · FALSE-claim fixes locked forever (1.3.1):
    import json as _json
    docs._ensure(docs.STATE)
    # #1 a REJECTED live test must keep `verify done` blocked — the reject-path bug (was: only 'handed_off').
    open(docs.VERIFY_STAMP, 'w').write(_json.dumps({'result': 'pass', 'ts': 0, 'deliverables': docs._deliverable_hash()}))
    open(docs.LIVETEST, 'w').write(_json.dumps({'state': 'handed_off'}))
    rc, out = _rc(docs.cmd_verify, action='done')
    if rc == 0:
        fails.append('livetest: a HANDED-OFF live test must block verify done')
    open(docs.LIVETEST, 'w').write(_json.dumps({'state': 'rejected'}))
    rc, out = _rc(docs.cmd_verify, action='done')
    if rc == 0 or 'REJECTED' not in out:
        fails.append('livetest: a REJECTED live test must keep verify done BLOCKED (the reject-path bug)')
    open(docs.LIVETEST, 'w').write(_json.dumps({'state': 'confirmed'}))
    rc, out = _rc(docs.cmd_verify, action='done')
    if rc != 0:
        fails.append('livetest: a CONFIRMED live test must UNBLOCK verify done')
    os.remove(docs.LIVETEST)
    # #2 route check is ADVISORY — flags mis-routed items loudly but exits 0 ("detects + surfaces, never blocks").
    open(docs.SESSION_MODEL, 'w').write('opus')
    _json.dump({'plan': 'scrape 500 vendor pages and dedupe the rows', 'hash': 'x', 'ts': 0, 'approved': True},
               open(docs.CONTRACT, 'w'))
    rc, out = _rc(docs.cmd_route, action='check')
    if 'ROUTE CHECK' not in out:
        fails.append('route check: must still surface mis-routed items loudly')
    if rc != 0:
        fails.append('route check: must be ADVISORY (exit 0) even when items are flagged (was falsely exit 1)')
    os.remove(docs.SESSION_MODEL)

    # T4 · roadmap self-contradiction detector — advisory (never blocking), fires ONLY on undecided+has-choice.
    open(os.path.join(root, 'docs', 'roadmap.md'), 'w').write(
        '# Roadmap\n\n## North star\nship it\n\n## Checkpoints\n'
        '1. [reached] niche\n   - micro-niche chosen\n'
        '2. [undecided] access layer\n   - FastAPI CRUD BUILT + verified\n')  # undecided BUT has a choice = the lie
    rc, out = _rc(docs.cmd_rehydrate, full=False)
    if 'CONTRADICTS ITSELF' not in out:
        fails.append('T4 roadmap: an undecided checkpoint carrying a choice must be flagged (roadmap-lies-live)')
    if 'CONTRADICTS' in ''.join(x for x in out.splitlines() if x.startswith('[B')):
        fails.append('T4 roadmap: the contradiction must be ADVISORY, never a rehydrate BLOCKING item')
    # a CONSISTENT roadmap (undecided with no choice) must NOT be flagged — no cry-wolf
    open(os.path.join(root, 'docs', 'roadmap.md'), 'w').write(
        '# Roadmap\n\n## North star\nship it\n\n## Checkpoints\n1. [reached] niche\n   - chosen\n2. [active] access\n')
    rc, out = _rc(docs.cmd_rehydrate, full=False)
    if 'CONTRADICTS ITSELF' in out:
        fails.append('T4 roadmap: a consistent roadmap must NOT be flagged (cry-wolf)')
    os.remove(os.path.join(root, 'docs', 'roadmap.md'))
    # T4 · deliverables misconfig — only when a verify stamp exists AND the tracked dir is missing.
    import json as _json2
    open(docs.DELIVERABLES, 'w').write('nonexistent_output_dir\n')
    open(docs.VERIFY_STAMP, 'w').write(_json2.dumps({'result': 'pass', 'ts': 0, 'deliverables': 'x'}))
    rc, out = _rc(docs.cmd_rehydrate, full=False)
    if 'DELIVERABLES MISCONFIGURED' not in out:
        fails.append('T4 deliverables: a verify-tracked dir that is missing must be flagged (inert staleness net)')
    os.remove(docs.VERIFY_STAMP)  # without a verify workflow, the same misconfig must stay SILENT
    rc, out = _rc(docs.cmd_rehydrate, full=False)
    if 'DELIVERABLES MISCONFIGURED' in out:
        fails.append('T4 deliverables: must NOT nag a project that is not using verify (cry-wolf)')
    open(docs.DELIVERABLES, 'w').write('data\n')
    # T6 · discuss opens a multi-part input as a SET; build gate holds until EVERY part is closed.
    for r in docs._load_jsonl(docs.DISCUSS):
        pass
    open(docs.DISCUSS, 'w').close()  # reset thread state from the earlier discuss test
    _rc(docs.cmd_discuss, action='open', thread=['part A', 'part B', 'part C'], id=None, choice=None, to_decision=None)
    openn = [r for r in docs._load_jsonl(docs.DISCUSS) if r.get('status') == 'open']
    if len(openn) != 3:
        fails.append(f'T6 discuss: one multi-thread open must arm all parts (got {len(openn)}, expected 3)')
    docs._ensure(docs.STATE)
    _json2.dump({'plan': 'x', 'hash': 'x', 'ts': 0, 'approved': True}, open(docs.CONTRACT, 'w'))
    rc, out = _rc(docs.cmd_contract, action='check', content=None, from_file=None, approved=False, window=None)
    if rc == 0:
        fails.append('T6 discuss: build must stay gated while any of the multi-part threads is open')
    _rc(docs.cmd_discuss, action='close', id=openn[0]['id'], choice=None, to_decision=None, thread=None)
    rc, out = _rc(docs.cmd_contract, action='check', content=None, from_file=None, approved=False, window=None)
    if rc == 0:
        fails.append('T6 discuss: closing ONE of three parts must not release the gate (2 still open)')

    # Point 3 · thread-age marker: a lingering open thread gets a factual '(open Nd)' past a 2-day threshold;
    # a same-session (fresh) thread stays clean so the surface never becomes cry-wolf noise (points 4/7 ethos).
    _tnow = docs.time.time()
    if docs._thread_age_note({'ts': _tnow - 5 * 86400}) != '  (open 5d)':
        fails.append('thread-age: a 5-day-old open thread must be marked (open 5d)')
    if docs._thread_age_note({'ts': _tnow}) != '':
        fails.append('thread-age: a fresh (same-session) thread must stay clean — no age note (anti-cry-wolf)')
    if docs._thread_age_note({'ts': _tnow - 86400}) != '':
        fails.append('thread-age: under the 2-day threshold must stay clean')
    if docs._thread_age_note({}) != '':
        fails.append('thread-age: a record with no ts must be silently skipped')

    # T8 · status is a pure READOUT — clean panel + one-line form, and it NEVER gates (always exit 0),
    # even under a freeze/blocking state that makes rehydrate/contract exit non-zero.
    rc, out = _rc(docs.cmd_status, line=False)
    if rc != 0 or 'IN MEMORY' not in out or 'OPEN NOW' not in out:
        fails.append(f'status: full panel must exit 0 and show IN MEMORY + OPEN NOW (rc={rc})')
    rc, out = _rc(docs.cmd_status, line=True)
    if rc != 0 or out.count('\n') != 1 or not out.startswith('▸'):
        fails.append(f'status --line: must be a single line starting with ▸ (rc={rc}, lines={out.count(chr(10))})')
    if 'last:' not in out:  # point-1: the line must SHOW the last captured record, so the agent relays it (not hand-write)
        fails.append('status --line: must name the last captured record (last: …) when records exist — the fabrication fix')

    # Fresh-capture (user idea): first presence is conservative ("last:", not "just saved" — a pre-existing record
    # isn't news); a capture made SINCE a prior presence flips to "✓ just saved", then reverts (reported once).
    _saved_ls = docs.LAST_STATUS
    docs.LAST_STATUS = os.path.join(root, '.keel', '.last_status_test')
    if os.path.exists(docs.LAST_STATUS):
        os.remove(docs.LAST_STATUS)
    _rc0, _o1 = _rc(docs.cmd_status, line=True)
    if '✓ just saved' in _o1 or 'last:' not in _o1:
        fails.append('fresh-capture: the FIRST presence must say "last:", never "just saved" (no marker yet)')
    _newdec = os.path.join(root, 'docs', 'decisions', '0099-fresh.md')
    open(_newdec, 'w').write('# 0099 — a fresh call\nStatus: accepted\n')
    os.utime(_newdec, (docs.time.time() + 1000, docs.time.time() + 1000))  # strictly-later than the marker
    _rc0, _o2 = _rc(docs.cmd_status, line=True)
    if '✓ just saved' not in _o2:
        fails.append('fresh-capture: a record written since the last presence must show "✓ just saved"')
    _rc0, _o3 = _rc(docs.cmd_status, line=True)
    if '✓ just saved' in _o3:
        fails.append('fresh-capture: nothing new since ⇒ must revert to "last:" (a capture is reported once)')
    os.remove(_newdec)
    docs.LAST_STATUS = _saved_ls
    open(docs.STANCE, 'w').write(_json.dumps({'name': 'freeze', 'freeze': True}))  # blocking state...
    rc, out = _rc(docs.cmd_status, line=False)
    if rc != 0:
        fails.append('status: must stay a readout (exit 0) even under an active freeze — it never gates')
    if 'FREEZE' not in out:
        fails.append('status: an active freeze must show in the panel')
    os.remove(docs.STANCE)
    # 1.4.1 · status must never be a FACADE: an undecided-with-choice checkpoint is a self-contradiction and
    # MUST surface (as [!] in the bar + a NEEDS RECONCILING count), and --line must carry a ⚠ marker.
    open(os.path.join(root, 'docs', 'roadmap.md'), 'w').write(
        '# Roadmap\n\n## North star\nship it\n\n## Checkpoints\n'
        '1. [reached] a\n   - done\n2. [undecided] b\n   - BUILT + verified\n')  # undecided BUT has a choice
    rc, out = _rc(docs.cmd_status, line=False)
    if '[!]' not in out or 'NEEDS RECONCILING' not in out or 'self-contradict' not in out:
        fails.append('status: an undecided-with-choice checkpoint must show as [!] + NEEDS RECONCILING (no facade)')
    rc, lout = _rc(docs.cmd_status, line=True)
    if '⚠' not in lout:
        fails.append('status --line: must carry a ⚠ marker when integrity issues exist (never look clean while hiding them)')
    # a CONSISTENT roadmap (undecided, no choice) must NOT trip the contradiction signal
    open(os.path.join(root, 'docs', 'roadmap.md'), 'w').write(
        '# Roadmap\n\n## North star\nship it\n\n## Checkpoints\n1. [reached] a\n   - done\n2. [active] b\n')
    rc, out = _rc(docs.cmd_status, line=False)
    if 'self-contradict' in out:
        fails.append('status: a consistent roadmap must NOT report a contradiction (cry-wolf)')
    os.remove(os.path.join(root, 'docs', 'roadmap.md'))

    # Point 2 · version-change notice + G3 (mid-session reach): the split helpers let SEVERAL surfaces detect
    # the same bump but advance the marker exactly once. _version_bump = PURE check (no write); _mark_version_seen
    # advances; _version_notice = text + advance. First run silent (byte-parity); same version never re-notices;
    # 'unknown' inert. G3 adds: pure-check is repeatable, and the bump is consumed once the marker advances.
    _saved_ls, _saved_ver = docs.LAST_SEEN, docs.KEEL_VERSION
    docs.LAST_SEEN = os.path.join(root, '.last_seen_test')
    if os.path.exists(docs.LAST_SEEN):
        os.remove(docs.LAST_SEEN)
    docs.KEEL_VERSION = '9.9.9'
    if docs._version_notice() is not None:
        fails.append('version-notice: first run on an install (no marker) must be SILENT')
    if open(docs.LAST_SEEN).read().strip() != '9.9.9':
        fails.append('version-notice: first run must still record the current version to the marker')
    if docs._version_notice() is not None:
        fails.append('version-notice: the same version must not re-notice (one-time per bump)')
    docs.KEEL_VERSION = '9.9.10'
    if docs._version_bump() != ('9.9.9', '9.9.10') or docs._version_bump() != ('9.9.9', '9.9.10'):
        fails.append('G3: _version_bump must detect the bump WITHOUT advancing (pure, repeatable across surfaces)')
    _n = docs._version_notice()
    if not _n or 'keel updated 9.9.9 → 9.9.10' not in _n or '/keel' not in _n:
        fails.append('version-notice: a version bump must announce X → Y and nudge a /keel reload')
    if open(docs.LAST_SEEN).read().strip() != '9.9.10':
        fails.append('version-notice: the marker must advance to the new version after the notice')
    if docs._version_bump() is not None:
        fails.append('G3: once the marker advances, the bump is consumed — the update fires exactly once total')
    docs.KEEL_VERSION = 'unknown'
    if docs._version_notice() is not None or open(docs.LAST_SEEN).read().strip() != '9.9.10':
        fails.append("version-notice: an 'unknown' version must neither notice nor overwrite the marker")
    docs.KEEL_VERSION, docs.LAST_SEEN = _saved_ver, _saved_ls

    # Wave A · cwd/ROOT anchor (the silent-memory-loss fix) + journal forgiveness.
    _here = os.getcwd()
    projp = tempfile.mkdtemp(prefix='keel-root-'); os.makedirs(os.path.join(projp, '.keel'))
    os.makedirs(os.path.join(projp, 'sub', 'deep')); freshp = tempfile.mkdtemp(prefix='keel-fresh-')
    try:
        os.chdir(os.path.join(projp, 'sub', 'deep'))
        if os.path.realpath(docs._resolve_root()) != os.path.realpath(projp):
            fails.append('cwd anchor: _resolve_root must climb to the nearest ancestor .keel (subdir-drift fix)')
        os.chdir(freshp)
        if os.path.realpath(docs._resolve_root()) != os.path.realpath(freshp):
            fails.append('cwd anchor: with no ancestor .keel, _resolve_root must return cwd (fresh project)')
        os.environ['KEEL_ROOT'] = projp
        if os.path.realpath(docs._resolve_root()) != os.path.realpath(projp):
            fails.append('cwd anchor: KEEL_ROOT env must override')
        os.environ.pop('KEEL_ROOT', None)
        # home-cap: a stray .keel AT $HOME must NOT capture a project below it (the over-climb footgun)
        fakehome = tempfile.mkdtemp(prefix='keel-home-'); os.makedirs(os.path.join(fakehome, '.keel'))
        os.makedirs(os.path.join(fakehome, 'p', 'q')); _oldhome = os.environ.get('HOME')
        os.environ['HOME'] = fakehome; os.chdir(os.path.join(fakehome, 'p', 'q'))
        if os.path.realpath(docs._resolve_root()) != os.path.realpath(os.path.join(fakehome, 'p', 'q')):
            fails.append('cwd anchor: a stray .keel AT $HOME must not capture a project below it (over-climb footgun)')
        (os.environ.__setitem__('HOME', _oldhome) if _oldhome is not None else os.environ.pop('HOME', None))
        # KEEL_ROOT at a nonexistent path must EXIT loudly, not silently create a stray tree
        os.environ['KEEL_ROOT'] = os.path.join(freshp, 'does-not-exist')
        try:
            docs._resolve_root(); fails.append('cwd anchor: KEEL_ROOT at a nonexistent path must exit, not proceed')
        except SystemExit:
            pass
        os.environ.pop('KEEL_ROOT', None)
    finally:
        os.chdir(_here)
    import types as _types
    _b = io.StringIO()
    with contextlib.redirect_stdout(_b):
        docs.cmd_journal(_types.SimpleNamespace(text='shipped the auth layer today', title=None,
                                                content=None, from_file=None, draft=False, friction=None))
    _jrn = docs._journals_sorted()
    if not _jrn or 'shipped-the-auth' not in os.path.basename(_jrn[-1]):
        fails.append('journal forgiveness: a bare positional note must create a journal with a derived title')
    # 1.4.2 adversarial-audit hardening: guard keys on the canonical INSTALL AREA (~/.claude/skills), so a
    # vendored/dev copy of docs.py inside a real project stays usable; and --from is never discarded.
    _skills = os.path.realpath(os.path.expanduser(os.path.join('~', '.claude', 'skills')))
    if not docs._in_install_area(os.path.join(_skills, 'keel')):
        fails.append('guard: a path under ~/.claude/skills must be flagged as the install area')
    if docs._in_install_area(root):
        fails.append('guard: a real project dir must NOT be flagged as the install area (would block vendored/dev use)')
    _fp = os.path.join(root, 'body.md'); open(_fp, 'w').write('## Context\nprepared body text\n')
    _b4 = io.StringIO()
    with contextlib.redirect_stdout(_b4):
        docs.cmd_decision(_types.SimpleNamespace(text='short label', title=None, content=None, from_file=_fp, draft=False))
    _lastdec = sorted(docs._decisions())[-1]
    if 'prepared body text' not in open(_lastdec).read():
        fails.append('decision: --from body must NOT be discarded when a positional label is also given')
    if 'short-label' not in os.path.basename(_lastdec):
        fails.append('decision: the positional should become the label when --from supplies the body')

    # G1 title extraction: a decision with NO '# ' heading (body uses ## Decision, real case: faire-lead/0013)
    # must de-slug the filename, never surface the raw hyphenated slug — the "show keel's title" doctrine
    # relies on titles being clean. (0014-style: a '# ' heading below a '> SUPERSEDED' banner is found fine.)
    _nh = os.path.join(root, 'docs', 'decisions', '0042-async-worker-model-deferred-scoring.md')
    open(_nh, 'w').write('> **SUPERSEDED**\n\n## Context\nx\n\n## Decision — async model\ny\n')
    _ent = next((e for e in docs._dec_entries() if e['src'].endswith('0042-async-worker-model-deferred-scoring.md')), None)
    if not _ent or _ent['title'] != '0042 — async worker model deferred scoring':
        fails.append(f"title fallback: a no-#-heading decision must de-slug the filename, got {_ent and _ent['title']!r}")
    os.remove(_nh)

    if fails:
        print('SELFTEST FAILED:')
        for f in fails:
            print('  - ' + f)
        sys.exit(1)
    print('SELFTEST PASSED — contradiction + suspect detectors precise '
          f'(contra={sorted(contra)}, suspect={sorted(suspect)})')


if __name__ == '__main__':
    main()
