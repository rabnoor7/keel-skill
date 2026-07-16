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
    for cmdname in ('rehydrate', 'layout', 'feedback', 'run', 'sink', 'stance', 'escalate', 'ask', 'discuss'):
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

    if fails:
        print('SELFTEST FAILED:')
        for f in fails:
            print('  - ' + f)
        sys.exit(1)
    print('SELFTEST PASSED — contradiction + suspect detectors precise '
          f'(contra={sorted(contra)}, suspect={sorted(suspect)})')


if __name__ == '__main__':
    main()
