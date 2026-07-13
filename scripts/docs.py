#!/usr/bin/env python3
"""keel — deterministic project-memory + enforcement CLI.

The skill's prose motivates and routes; THIS file enforces. Correctness-critical invariants live here as
checks that run inbound on `rehydrate` and FAIL LOUDLY, so they don't depend on the model remembering.

Layout (under the project root = cwd):
  docs/architecture.md · data-model.md · decisions/NNNN-*.md · journal/YYYY-MM-DD-*.md
  memory/*.md            project memory (also auto-found in ~/.claude/projects/<slug>/memory/ + custom paths)
  archive/inputs · archive/scratch   rebuildable source + deletable scratch (deliverables stay clean)
  .keel/                 gitignored state: pending/, contract.json, verify.stamp, deliverables, profile, ...
Global prefs: ~/keel/preferences.md.

Commands: init · rehydrate · hydrate · profile · decision · journal · supersede · contradictions ·
          contract · verify · hygiene · friction · clarify-depth · claim · whiteboard · search · read · prefs · state
"""
import argparse, os, sys, json, re, hashlib, time, datetime, glob, fcntl
from collections import defaultdict

ROOT = os.getcwd()
DOCS = os.path.join(ROOT, 'docs')
DEC = os.path.join(DOCS, 'decisions')
JRN = os.path.join(DOCS, 'journal')
MEM = os.path.join(ROOT, 'memory')
STATE = os.path.join(ROOT, '.keel')
PENDING = os.path.join(STATE, 'pending.jsonl')
CONTRACT = os.path.join(STATE, 'contract.json')
PROFILE = os.path.join(STATE, 'profile')
WHITEBOARD = os.path.join(STATE, 'whiteboard.log')
CLAIMS = os.path.join(STATE, 'claims')
VERIFY_DIR = os.path.join(STATE, 'verify')
VERIFY_STAMP = os.path.join(STATE, 'verify.stamp')
CLARIFY = os.path.join(STATE, 'clarify_depth')
DELIVERABLES = os.path.join(STATE, 'deliverables')
ANCHOR = os.path.join(DOCS, 'architecture.md')
GLOBAL = os.path.expanduser('~/keel/preferences.md')
PROFILES = ('web-app', 'data-pipeline', 'automation', 'cli-tool', 'ml')
# A supersession CLAIM (not mere co-occurrence). Two grammatical shapes, both requiring the ADR to be the
# verb's object — so "override files … see ADR 14" and "do NOT web-search … ADR 13" stay clean.
_ADRREF = r'ADR[- ]?0*(\d{1,4})'
CONTRA_A = re.compile(rf'(?:supersed\w*|replac\w*|revers\w*|overrid\w*)[\s:—–-]{{0,3}}{_ADRREF}', re.I)  # verb→ADR
CONTRA_B = re.compile(rf'{_ADRREF}\s+(?:is\s+|was\s+|now\s+){{0,3}}(?:supersed\w*|replaced|reversed|overridden|no\s+longer)\b', re.I)  # ADR→dead
# Skill-dir-relative (NOT project ROOT): the one-time post-install intro marker lives with the skill itself,
# so it fires on first use after an install and self-suppresses forever after — per install, not per project.
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRO_MARKER = os.path.join(SKILL_ROOT, '.introduced')


def _now(): return datetime.datetime.now()


def _read(p):
    try:
        with open(p, encoding='utf-8') as f:
            return f.read()
    except OSError:
        return ''


def _ensure(*dirs):
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def _mtime(p):
    try:
        return os.path.getmtime(p)
    except OSError:
        return 0


def _hash(s): return hashlib.sha256(s.encode('utf-8', 'ignore')).hexdigest()[:12]
def _slug(t): return re.sub(r'[^a-z0-9]+', '-', t.lower()).strip('-')[:60] or 'entry'


def _append_jsonl(p, obj):
    _ensure(os.path.dirname(p))
    with open(p, 'a', encoding='utf-8') as f:
        f.write(json.dumps(obj) + '\n')


def _load_jsonl(p):
    out = []
    for line in _read(p).splitlines():
        if line.strip():
            try: out.append(json.loads(line))
            except ValueError: pass
    return out


def _slugify_root():
    return re.sub(r'[/.]', '-', ROOT)  # mirror Claude Code's project-memory dir naming


def _memory_dirs():
    """All existing project-memory dirs — memory lives in different places across repos, so scan them all."""
    cands = [MEM, os.path.expanduser(os.path.join('~/.claude/projects', _slugify_root(), 'memory'))]
    cfg = os.path.join(STATE, 'memory-paths')
    if os.path.exists(cfg):
        cands += [os.path.expanduser(x.strip()) for x in _read(cfg).splitlines() if x.strip()]
    if os.environ.get('KEEL_MEMORY'):
        cands.append(os.path.expanduser(os.environ['KEEL_MEMORY']))
    seen, out = set(), []
    for d in cands:
        d = os.path.abspath(d)
        if d not in seen and os.path.isdir(d):
            seen.add(d); out.append(d)
    return out


def _memory_files():
    return [p for d in _memory_dirs() for p in glob.glob(os.path.join(d, '*.md'))]


def _deliverable_dirs():
    return [x.strip() for x in _read(DELIVERABLES).splitlines() if x.strip()] or ['data']


def _deliverable_hash():
    """Hash of declared deliverable files' mtimes — changes whenever a deliverable changes (read-only)."""
    files = []
    for d in _deliverable_dirs():
        files += glob.glob(os.path.join(ROOT, d, '**', '*'), recursive=True)
    return _hash('|'.join(sorted(f'{os.path.relpath(p, ROOT)}:{_mtime(p)}:{os.path.getsize(p)}'
                                 for p in files if os.path.isfile(p))))


def _hygiene_problems():
    """Deliverables = finals only; flag junk pile-up + same-artifact drift (read-only). G2."""
    probs = []
    for d in _deliverable_dirs():
        files = [os.path.basename(p) for p in glob.glob(os.path.join(ROOT, d, '*')) if os.path.isfile(p)
                 and not os.path.basename(p).startswith('.')]
        stems = defaultdict(list)
        for f in files:
            stems[re.split(r'[_.\- ]', f)[0].lower()].append(f)
        for stem, fs in stems.items():
            if len(fs) > 2:
                probs.append(f'{d}/: {len(fs)} files share stem "{stem}" ({fs[:4]}) — same artifact drifting? declare one canonical.')
        if len(files) > 40:
            probs.append(f'{d}/ holds {len(files)} files — deliverables are finals only; move intermediates to archive/.')
    return probs


# ---------------- init ----------------

def cmd_init(a):
    _ensure(DOCS, DEC, JRN, MEM, STATE, CLAIMS, VERIFY_DIR,
            os.path.join(ROOT, 'archive', 'inputs'), os.path.join(ROOT, 'archive', 'scratch'))
    if not os.path.exists(DELIVERABLES):
        open(DELIVERABLES, 'w').write('data\n')  # finals live here; intermediates/scratch → archive/
    if not os.path.exists(ANCHOR):
        with open(ANCHOR, 'w') as f:
            f.write('# Architecture — REHYDRATION ANCHOR\n\n'
                    '> Fresh session? Run `python3 <skill>/scripts/docs.py rehydrate`. Read this first,\n'
                    '> then decisions/, then the newest journal.\n\n## What this is\n(fill in)\n\n'
                    '## Current state\n(kept live via `hydrate`)\n')
    gi = os.path.join(ROOT, '.gitignore')
    if '.keel/' not in _read(gi):
        with open(gi, 'a') as f:
            f.write('\n.keel/\n')
    print(f'init: scaffolded docs/, memory/, archive/{{inputs,scratch}}, .keel/ under {ROOT}')


# ---------------- checks (the reliability core) ----------------

def _decisions(): return sorted(glob.glob(os.path.join(DEC, '*.md')))


def _anchor_staleness():
    if not os.path.exists(ANCHOR):
        return None
    am = _mtime(ANCHOR)
    newer = [os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(DOCS, '**', '*.md'), recursive=True)
             if p != ANCHOR and _mtime(p) > am + 1]
    newer += [(os.path.relpath(p, ROOT) if p.startswith(ROOT) else p) for p in _memory_files() if _mtime(p) > am + 1]
    return newer


def _contradictions():
    hits = []
    tiers = [('memory', p) for p in _memory_files()] + [('journal', p) for p in glob.glob(os.path.join(JRN, '*.md'))]
    if os.path.exists(GLOBAL):
        tiers.append(('prefs', GLOBAL))
    dec_text = {os.path.basename(p): _read(p) for p in _decisions()}
    for tier, p in tiers:
        for line in _read(p).splitlines():
            m = CONTRA_A.search(line) or CONTRA_B.search(line)
            if m:
                n = int(m.group(1))
                target = next((t for f, t in dec_text.items() if re.match(rf'0*{n}\b', f)), None)
                if target is not None and not re.search(r'supersed', target, re.I):
                    rel = os.path.relpath(p, ROOT) if p.startswith(ROOT) else p
                    hits.append((tier, rel, n, line.strip()[:110]))
    return hits


def _suspect_decisions():
    # P is suspect if another ADR, on a SINGLE line, both uses a supersede verb AND names P as an explicit
    # "ADR <num>" reference — and P isn't self-marked superseded. Same-line + explicit ADR-ref is what keeps
    # "supersedes the too_big idea; refines 0009" from falsely retiring 0009 (0009 is the object of refines,
    # and a bare number isn't an ADR reference). A cross-line/bare-number match was the old false-positive.
    sus = []
    for p in _decisions():
        t = _read(p)
        m = re.match(r'0*(\d+)', os.path.basename(p))
        if not m or re.search(r'supersed', t, re.I):
            continue
        num = m.group(1)
        ref = re.compile(rf'ADR[- ]?0*{num}\b', re.I)
        for q in _decisions():
            if q == p:
                continue
            if any(re.search(r'supersed\w*', ln, re.I) and ref.search(ln) for ln in _read(q).splitlines()):
                sus.append(os.path.basename(p))
                break
    return sorted(set(sus))


# ---------------- rehydrate (INBOUND gate — read-only) ----------------

INTRO_TEXT = """\
======================================================================
  keel is installed — your disciplined engineering partner.
======================================================================

keel helps you BUILD and EVOLVE software of any kind — web apps, data pipelines,
scraping/automation, CLI tools, ML. It is not a code vending machine: it maps
before it writes, clarifies before it codes, and verifies before it says "done."

THE LOOP
  rehydrate -> [discuss <-> clarify] -> build (behind a contract) -> verify -> hydrate
  - rehydrate  on an existing project it reads your docs/ memory first (READ-ONLY)
  - clarify    asks only what it genuinely can't resolve itself — in plain language,
               tradeoffs spelled out — then shows you a build contract
  - build      only after you approve that contract
  - verify     checks the real deliverable, not its own claim, before "done"
  - hydrate    writes decisions + corrections to durable memory as they happen

WHAT THAT FEELS LIKE
  - it won't fabricate data or claim something works without checking
  - it asks before big or costly actions, and keeps your project folder tidy
  - it remembers decisions across sessions, so you don't re-explain yourself

TO START
  Just tell it what you want to build or change. On an existing project, say
  "rehydrate" (or start describing the work) and it loads context first.

The rules that must not drift live in code, not prose:  python3 scripts/docs.py --help
======================================================================"""


def _maybe_intro():
    """Print the one-time post-install introduction; return True if it fired. The marker lives in the skill
    dir (per-install, not per-project), so this shows once on first use after an install, then stays silent."""
    if os.path.exists(INTRO_MARKER):
        return False
    print(INTRO_TEXT)
    try:
        with open(INTRO_MARKER, 'w') as fh:
            fh.write(_now().isoformat() + '\n')
    except OSError:
        pass
    return True


def cmd_intro(a):
    if getattr(a, 'force', False):
        try:
            os.remove(INTRO_MARKER)
        except OSError:
            pass
    if not _maybe_intro():
        print(f'keel already introduced on this install (marker: {INTRO_MARKER}). Use --force to show it again.')


def cmd_rehydrate(a):
    problems = 0
    if _maybe_intro():
        print()
    print('=' * 70); print('KEEL REHYDRATE — digest across all tiers'); print('=' * 70)
    print(f'\nPROFILE: {_read(PROFILE).strip() or "(unset — run: docs.py profile <name>)"}')
    mdirs = _memory_dirs()
    print('MEMORY tiers found: ' + (', '.join((os.path.relpath(d, ROOT) if d.startswith(ROOT) else d) for d in mdirs) or '(none)'))

    if os.path.exists(ANCHOR):
        print('\n--- ANCHOR (docs/architecture.md) ---\n' + '\n'.join(_read(ANCHOR).splitlines()[:18]))
    else:
        print('\n(no docs/architecture.md — run docs.py init)')

    decs = _decisions()
    print(f'\n--- DECISIONS: {len(decs)} ADR(s) ---')
    for d in decs[-12:]:
        title = next((l for l in _read(d).splitlines() if l.strip()), os.path.basename(d))
        print('   ' + title.strip('# ').strip()[:88])

    stale = _anchor_staleness()
    if stale:
        problems += 1
        print(f'\n[!] ANCHOR STALE — {len(stale)} file(s) changed after the anchor: {stale[:6]}')
        print('    → the first thing a session reads is behind reality. Run `hydrate` to refresh it.')

    contra = _contradictions()
    if contra:
        problems += 1
        print(f'\n[!!] CONTRADICTIONS — {len(contra)} lower-tier correction(s) supersede an unmarked ADR:')
        for tier, path, n, line in contra[:8]:
            print(f'    ADR {n}: {tier}:{path} says "{line}"')
        print(f'    → do NOT act on the stale ADR. Resolve with `docs.py supersede {contra[0][2]}` first.')

    sus = _suspect_decisions()
    if sus:
        print(f'\n[!] SUSPECT (referenced as superseded, not marked): {sus}')

    pend = [x for x in _load_jsonl(PENDING) if not x.get('drained')]
    if pend:
        problems += 1
        print(f'\n[!] {len(pend)} UNFLUSHED item(s) from a prior session (visible debt):')
        for x in pend[-6:]:
            print(f'    {x.get("kind")}: {x.get("title", "")[:80]}' + ('  (DRAFT)' if x.get('staged') else ''))
        print('    → run `docs.py hydrate` to land/drain them.')

    if os.path.exists(VERIFY_STAMP):
        s = json.load(open(VERIFY_STAMP))
        if s.get('result') != 'pass' or s.get('deliverables') != _deliverable_hash():
            problems += 1
            print('\n[!] VERIFY STALE/FAILED — the deliverable is not covered by a fresh passing audit.')
            print('    → run `docs.py verify run`; "done" is gated on it (`verify done`).')

    hyg = _hygiene_problems()
    if hyg:
        problems += 1
        print(f'\n[!] HYGIENE — {len(hyg)} issue(s), e.g.: {hyg[0]}')
        print('    → run `docs.py hygiene` for the full list.')

    js = sorted(glob.glob(os.path.join(JRN, '*.md')))
    print(f'\n--- newest journal --- ' + (os.path.basename(js[-1]) if js else '(none)'))
    print('\n' + '=' * 70)
    if problems:
        print(f'VERDICT: ⚠️  {problems} issue(s) — resolve before building. (exit 1)'); sys.exit(1)
    print('VERDICT: ✅ clean — rehydrated.')


# ---------------- decision / journal (draft-able; feed the pending queue) ----------------

def _next_adr():
    n = 0
    for p in _decisions() + glob.glob(os.path.join(STATE, 'pending', '*.md')):
        m = re.match(r'0*(\d+)', os.path.basename(p))
        if m:
            n = max(n, int(m.group(1)))
    return n + 1


def _emit_record(kind, fn_name, content, target_dir, draft, title, extra=None):
    rec = {'kind': kind, 'title': title, 'ts': time.time()}
    if extra:
        rec.update(extra)
    if draft:
        _ensure(os.path.join(STATE, 'pending'))
        staged = os.path.join(STATE, 'pending', fn_name)
        open(staged, 'w').write(content)
        rec['staged'] = staged
        rec['target'] = os.path.join(target_dir, fn_name)
        _append_jsonl(PENDING, rec)
        print(f'{kind} DRAFTED → {os.path.relpath(staged, ROOT)} — lands in docs/ only on approval (`hydrate`).')
    else:
        _ensure(target_dir)
        open(os.path.join(target_dir, fn_name), 'w').write(content)
        _append_jsonl(PENDING, rec)
        print(f'{kind}: wrote {os.path.relpath(os.path.join(target_dir, fn_name), ROOT)} (queued for hydrate)')


def cmd_decision(a):
    n = _next_adr()
    body = a.content or (a.from_file and _read(a.from_file)) or '## Context\n\n## Decision\n\n## Rejected\n'
    _emit_record('decision', f'{n:04d}-{_slug(a.title)}.md', f'# {n:04d} — {a.title}\n\n{body}\n',
                 DEC, a.draft, a.title, {'n': n})


def cmd_journal(a):
    fn = f'{_now():%Y-%m-%d}-{_slug(a.title)}.md'
    content = f'# {a.title}\n\n{a.content or (a.from_file and _read(a.from_file)) or ""}\n\nfriction: {a.friction or "(none)"}\n'
    _emit_record('journal', fn, content, JRN, a.draft, a.title)


def cmd_supersede(a):
    old = next((p for p in _decisions() if re.match(rf'0*{a.number}\b', os.path.basename(p))), None)
    if not old:
        sys.exit(f'no ADR {a.number} found')
    t = _read(old)
    if not re.search(r'supersed', t, re.I):
        open(old, 'w').write('> **SUPERSEDED — see the newer ADR.**\n\n' + t)
    n = _next_adr()
    body = a.content or (a.from_file and _read(a.from_file)) or f'## Context\nSupersedes ADR {int(a.number):04d}.\n\n## Decision\n\n## Rejected\n'
    fn = os.path.join(DEC, f'{n:04d}-{_slug(a.title)}.md')
    open(fn, 'w').write(f'# {n:04d} — {a.title}\n\n> Supersedes ADR {int(a.number):04d}.\n\n{body}\n')
    _append_jsonl(PENDING, {'kind': 'decision', 'n': n, 'title': a.title, 'ts': time.time()})
    print(f'supersede: marked ADR {int(a.number):04d}, wrote superseding {os.path.relpath(fn, ROOT)}')


# ---------------- hydrate (OUTBOUND — lands approved drafts, drains queue) ----------------

def cmd_hydrate(a):
    pend = _load_jsonl(PENDING)
    live = [x for x in pend if not x.get('drained')]
    landed = 0
    for x in live:
        st, tgt = x.get('staged'), x.get('target')
        if st and tgt and os.path.exists(st):
            _ensure(os.path.dirname(tgt)); os.rename(st, tgt); landed += 1
    print(f'hydrate: {len(live)} pending item(s), {landed} approved draft(s) landed into docs/.')
    for x in live:
        print(f'   {x.get("kind")}: {x.get("title", "")[:80]}')
    with open(PENDING, 'w') as f:
        for x in pend:
            x['drained'] = True; f.write(json.dumps(x) + '\n')
    if os.path.exists(ANCHOR):
        os.utime(ANCHOR, None)
    print('hydrate: queue drained; anchor freshness refreshed.')
    print('   REMINDER: if any item CORRECTED a prior ADR, run `docs.py supersede <n>` — a correction left '
          'only in journal/memory is invisible to the next rehydrate.')


# ---------------- contract (build-START gate) ----------------

def cmd_contract(a):
    if a.action == 'set':
        plan = a.content or (a.from_file and _read(a.from_file)) or ''
        if not plan.strip():
            sys.exit('contract set: needs --content or --from (the plan text)')
        _ensure(STATE)
        json.dump({'plan': plan, 'hash': _hash(plan), 'ts': time.time(), 'approved': bool(a.approved)}, open(CONTRACT, 'w'))
        print(f'contract set (hash {_hash(plan)}, approved={bool(a.approved)}).'
              + ('' if a.approved else ' Get user approval, then: contract approve'))
    elif a.action == 'approve':
        if not os.path.exists(CONTRACT):
            sys.exit('no contract to approve — contract set first')
        c = json.load(open(CONTRACT)); c['approved'] = True; c['ts'] = time.time(); json.dump(c, open(CONTRACT, 'w'))
        print('contract approved — build may proceed.')
    elif a.action == 'check':
        if not os.path.exists(CONTRACT):
            print('contract check: NONE — no build without a signed contract.'); sys.exit(1)
        c = json.load(open(CONTRACT))
        fresh = (time.time() - c.get('ts', 0)) < (a.window or 3600)
        if c.get('approved') and fresh:
            print('contract check: ✅ signed + fresh.'); return
        print(f'contract check: ✗ approved={c.get("approved")} fresh={fresh} — do not build.'); sys.exit(1)


# ---------------- verify (build-END gate: ran + passed + right spec) ----------------

AUDIT_TMPL = '''#!/usr/bin/env python3
"""Deliverable audit — exits NON-ZERO on failure. The RATCHET: field-level completeness (never row-count),
provenance (anti-fabrication), and one regression assertion per bug ever fixed. Model LEGITIMATE absence."""
import sys
fails = []
# --- FIELD COMPLETENESS with per-field legitimate-null conditions (NOT one blanket threshold) ---
# import csv; rows = list(csv.DictReader(open("data/master.csv")))
# GATES = [  # (field, min_fill, applies_to)  -- applies_to encodes when the field SHOULD be present
#   ("id",        0.99, lambda r: True),
#   ("rating",    0.99, lambda r: int(r.get("review_count") or 0) > 0),  # 0-review rows legitimately blank
#   ("min_order", 0.00, lambda r: r.get("has_minimum") == "True"),       # no-minimum rows legitimately 0
# ]
# for field, thr, applies in GATES:
#   pool = [r for r in rows if applies(r)]; filled = sum(1 for r in pool if (r.get(field) or "").strip())
#   frac = filled/max(1,len(pool)); print(f"{field:16} {filled}/{len(pool)} ({frac:.0%})")
#   if frac < thr: fails.append(field)
# --- PROVENANCE: every DERIVED datum carries a source pointer; rows without one FAIL. ---
# --- REGRESSION ASSERTIONS: one per fixed bug so it can't silently return. ---
# assert all(len(r["reviews"]) >= min(int(r["review_count"]), 20) for r in rows), "reviews truncated (regressed)"
if fails:
    print("VERDICT: FAIL", fails); sys.exit(1)
print("VERDICT: pass")
'''


def cmd_verify(a):
    _ensure(VERIFY_DIR, STATE)
    ap = os.path.join(VERIFY_DIR, 'audit.py')
    if a.action == 'init':
        if not os.path.exists(ap):
            open(ap, 'w').write(AUDIT_TMPL)
        print(f'verify init: {os.path.relpath(ap, ROOT)} — fill in field-level + provenance + regression checks.')
    elif a.action == 'run':
        if not os.path.exists(ap):
            sys.exit('no audit — run: verify init')
        import subprocess
        r = subprocess.run([sys.executable, ap])
        json.dump({'result': 'pass' if r.returncode == 0 else 'fail', 'ts': time.time(),
                   'deliverables': _deliverable_hash()}, open(VERIFY_STAMP, 'w'))
        print(f'verify run: exit {r.returncode} (stamped)'); sys.exit(r.returncode)
    elif a.action == 'done':
        if not os.path.exists(VERIFY_STAMP):
            print('verify done: ✗ never verified — run `verify run` before claiming done.'); sys.exit(1)
        s = json.load(open(VERIFY_STAMP))
        if s.get('result') != 'pass':
            print('verify done: ✗ last verify FAILED — fix + re-run.'); sys.exit(1)
        if s.get('deliverables') != _deliverable_hash():
            print('verify done: ✗ deliverable CHANGED since the last passing verify — re-run `verify run`.'); sys.exit(1)
        print('verify done: ✅ a fresh passing audit covers the current deliverable.')
    elif a.action == 'sync':
        gated = set(re.findall(r'''["']([a-z][a-z0-9_]{2,})["']''', _read(ap)))
        declared = set(re.findall(r'\b([a-z][a-z0-9_]{2,})\b', _read(os.path.join(DOCS, 'data-model.md'))))
        stale = sorted(g for g in gated if g not in declared)
        print('verify sync — audit gates fields NOT declared in data-model.md (possibly stale/out-of-scope):')
        print('  ' + (', '.join(stale) if stale else '(none — all gated fields are declared)'))
        if stale:
            print('  → confirm each is still a real field; a gate on a removed/renamed field silently fails.')


def cmd_hygiene(a):
    probs = _hygiene_problems()
    if probs:
        print('hygiene: ✗'); [print('  ' + p) for p in probs]; sys.exit(1)
    print(f'hygiene: ✅ deliverable dir(s) {_deliverable_dirs()} clean.')


# ---------------- claim / whiteboard (multi-agent coordination) ----------------

def cmd_claim(a):
    _ensure(CLAIMS)
    lock = os.path.join(CLAIMS, _slug(a.resource) + '.lock')
    if a.release:
        try: os.remove(lock); print(f'released {a.resource}')
        except OSError: print(f'{a.resource} was not held')
        return
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        os.write(fd, f'{a.by or "agent"} {time.time()}'.encode()); os.close(fd)
        print(f'claimed {a.resource} (exclusive)')
    except FileExistsError:
        print(f'DENIED: {a.resource} already held by {_read(lock)[:40]}'); sys.exit(1)


def cmd_whiteboard(a):
    _ensure(STATE)
    if a.action == 'post':
        with open(WHITEBOARD, 'a') as f:
            fcntl.flock(f, fcntl.LOCK_EX); f.write(f'{_now():%H:%M:%S} {a.by or "agent"}: {a.message}\n'); fcntl.flock(f, fcntl.LOCK_UN)
        print('posted.')
    else:
        print(_read(WHITEBOARD) or '(whiteboard empty)')


# ---------------- profile / search / read / prefs / state / friction / clarify-depth ----------------

def cmd_profile(a):
    if a.name:
        if a.name not in PROFILES:
            sys.exit(f'profile must be one of {PROFILES}')
        _ensure(STATE); open(PROFILE, 'w').write(a.name); print(f'profile set: {a.name} — load profiles/{a.name}.md')
    else:
        print(_read(PROFILE).strip() or f'(unset) choose: {", ".join(PROFILES)}')


def cmd_contradictions(a):
    c = _contradictions()
    if not c:
        print('no cross-tier contradictions found.'); return
    for tier, path, n, line in c:
        print(f'ADR {n}: {tier}:{path} — "{line}"')
    sys.exit(1)


def cmd_search(a):
    hits = 0
    for p in glob.glob(os.path.join(DOCS, '**', '*.md'), recursive=True) + _memory_files():
        for i, line in enumerate(_read(p).splitlines(), 1):
            if a.term.lower() in line.lower():
                rel = os.path.relpath(p, ROOT) if p.startswith(ROOT) else p
                print(f'{rel}:{i}: {line.strip()[:100]}'); hits += 1
    if not hits:
        print(f'no match for "{a.term}"')


def cmd_read(a):
    for p in [ANCHOR, os.path.join(DOCS, 'data-model.md')]:
        if os.path.exists(p):
            print(f'\n===== {os.path.relpath(p, ROOT)} =====\n' + _read(p))
    for p in _decisions():
        print(f'\n===== {os.path.relpath(p, ROOT)} =====\n' + _read(p))
    js = sorted(glob.glob(os.path.join(JRN, '*.md')))[-(a.journal_limit or 5):]
    for p in js:
        print(f'\n===== {os.path.relpath(p, ROOT)} =====\n' + _read(p))
    if len(glob.glob(os.path.join(JRN, '*.md'))) > len(js):
        print(f'\n(showing latest {len(js)} journal entries — use `search` for older)')


def cmd_prefs(a):
    if a.append:
        _ensure(os.path.dirname(GLOBAL))
        with open(GLOBAL, 'a') as f:
            f.write('\n- ' + a.append + '\n')
        print('prefs: appended (global).')
    else:
        print(_read(GLOBAL) or '(no global prefs at ~/keel/preferences.md)')


def cmd_state(a):
    sp = os.path.join(STATE, 'scratch.md'); _ensure(STATE)
    if a.note:
        with open(sp, 'a') as f:
            f.write(f'- {a.note}\n')
        print('state: noted.')
    else:
        print(_read(sp) or '(no scratch state)')


def cmd_friction(a):
    notes = []
    for p in sorted(glob.glob(os.path.join(JRN, '*.md'))):
        for line in _read(p).splitlines():
            m = re.match(r'\s*friction:\s*(.+)', line, re.I)
            if m and m.group(1).strip().lower() not in ('', '(none)', 'none'):
                notes.append((os.path.basename(p)[:10], m.group(1).strip()))
    if not notes:
        print('no friction notes found (add them via `journal --friction "..."`).'); return
    print(f'{len(notes)} friction note(s) — where the skill helped or got in the way (newest first):')
    for date, note in reversed(notes):
        print(f'  [{date}] {note[:160]}')


def cmd_clarify(a):
    if a.level:
        _ensure(STATE); open(CLARIFY, 'w').write(a.level); print(f'clarify_depth = {a.level}')
    else:
        print((_read(CLARIFY).strip() or 'thorough') + '  (how hard to clarify before building; thorough = enumerate every open option)')


def main():
    ap = argparse.ArgumentParser(prog='docs.py', description='keel memory + enforcement CLI')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('init', 'rehydrate', 'hydrate', 'contradictions', 'friction'):
        sub.add_parser(name).set_defaults(fn=globals()[f'cmd_{name}'])
    p = sub.add_parser('intro'); p.add_argument('--force', action='store_true'); p.set_defaults(fn=cmd_intro)
    p = sub.add_parser('profile'); p.add_argument('name', nargs='?'); p.set_defaults(fn=cmd_profile)
    for name in ('decision', 'journal'):
        p = sub.add_parser(name); p.add_argument('--title', required=True); p.add_argument('--content')
        p.add_argument('--from', dest='from_file'); p.add_argument('--draft', action='store_true')
        p.set_defaults(fn=globals()[f'cmd_{name}'])
        if name == 'journal':
            p.add_argument('--friction')
    p = sub.add_parser('supersede'); p.add_argument('number', type=int); p.add_argument('--title', required=True)
    p.add_argument('--content'); p.add_argument('--from', dest='from_file'); p.set_defaults(fn=cmd_supersede)
    p = sub.add_parser('contract'); p.add_argument('action', choices=['set', 'approve', 'check'])
    p.add_argument('--content'); p.add_argument('--from', dest='from_file'); p.add_argument('--approved', action='store_true')
    p.add_argument('--window', type=int); p.set_defaults(fn=cmd_contract)
    p = sub.add_parser('verify'); p.add_argument('action', choices=['init', 'run', 'done', 'sync']); p.set_defaults(fn=cmd_verify)
    sub.add_parser('hygiene').set_defaults(fn=cmd_hygiene)
    p = sub.add_parser('clarify-depth'); p.add_argument('level', nargs='?', choices=['thorough', 'light']); p.set_defaults(fn=cmd_clarify)
    p = sub.add_parser('claim'); p.add_argument('resource'); p.add_argument('--by'); p.add_argument('--release', action='store_true'); p.set_defaults(fn=cmd_claim)
    p = sub.add_parser('whiteboard'); p.add_argument('action', choices=['post', 'read']); p.add_argument('message', nargs='?', default=''); p.add_argument('--by'); p.set_defaults(fn=cmd_whiteboard)
    p = sub.add_parser('search'); p.add_argument('term'); p.set_defaults(fn=cmd_search)
    p = sub.add_parser('read'); p.add_argument('--all', action='store_true'); p.add_argument('--journal-limit', type=int); p.set_defaults(fn=cmd_read)
    p = sub.add_parser('prefs'); p.add_argument('--append'); p.set_defaults(fn=cmd_prefs)
    p = sub.add_parser('state'); p.add_argument('--note'); p.set_defaults(fn=cmd_state)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
