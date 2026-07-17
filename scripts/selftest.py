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
    _c = dict(content=None, from_file=None, approved=False, window=None)
    _rc(docs.cmd_contract, action='set', **{**_c, 'content': 'plan', 'approved': True})
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

    # T8 · status is a pure READOUT — clean panel + one-line form, and it NEVER gates (always exit 0),
    # even under a freeze/blocking state that makes rehydrate/contract exit non-zero.
    rc, out = _rc(docs.cmd_status, line=False)
    if rc != 0 or 'IN MEMORY' not in out or 'OPEN NOW' not in out:
        fails.append(f'status: full panel must exit 0 and show IN MEMORY + OPEN NOW (rc={rc})')
    rc, out = _rc(docs.cmd_status, line=True)
    if rc != 0 or out.count('\n') != 1 or not out.startswith('▸'):
        fails.append(f'status --line: must be a single line starting with ▸ (rc={rc}, lines={out.count(chr(10))})')
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

    if fails:
        print('SELFTEST FAILED:')
        for f in fails:
            print('  - ' + f)
        sys.exit(1)
    print('SELFTEST PASSED — contradiction + suspect detectors precise '
          f'(contra={sorted(contra)}, suspect={sorted(suspect)})')


if __name__ == '__main__':
    main()
