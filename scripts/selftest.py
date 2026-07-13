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

    if fails:
        print('SELFTEST FAILED:')
        for f in fails:
            print('  - ' + f)
        sys.exit(1)
    print('SELFTEST PASSED — contradiction + suspect detectors precise '
          f'(contra={sorted(contra)}, suspect={sorted(suspect)})')


if __name__ == '__main__':
    main()
