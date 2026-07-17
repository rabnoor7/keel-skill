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

Commands: init · rehydrate · hydrate · profile · decision · journal · supersede · contradictions · contract ·
          verify · hygiene · friction · clarify-depth · claim · whiteboard · search · read · prefs · state ·
          layout · feedback · run · sink · stance · escalate · ask · match · preserve · orphans · smoke ·
          accept · route · critique · coverage · livetest · handoff · outcome · checkpoint
          (--version prints the installed version)
"""
import argparse, os, sys, json, re, hashlib, time, datetime, glob, platform
from collections import defaultdict
try:
    import fcntl  # Unix; on Windows the whiteboard degrades to unlocked appends (documented)
except ImportError:
    fcntl = None

ROOT = os.getcwd()
DOCS = os.path.join(ROOT, 'docs')
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
GLOBAL = os.path.expanduser('~/keel/preferences.md')
# Canonical slot paths — what `init` scaffolds for a brand-new project. The layout-aware ANCHOR/DEC/JRN are
# resolved below once the helpers exist; on a canonical repo they equal these, so writes stay byte-identical.
ANCHOR_CANON = os.path.join(DOCS, 'architecture.md')
DEC_CANON = os.path.join(DOCS, 'decisions')
JRN_CANON = os.path.join(DOCS, 'journal')
# Skill-feedback log — friction/wishes about keel ITSELF. Central cross-project corpus (survives reinstalls)
# + per-project mirror. Local only; never sent anywhere.
FEEDBACK_CENTRAL = os.path.expanduser('~/.claude/keel/feedback.jsonl')
FEEDBACK_LOCAL = os.path.join(STATE, 'feedback.jsonl')
PROFILES = ('web-app', 'data-pipeline', 'automation', 'cli-tool', 'ml', 'general')
# A supersession CLAIM (not mere co-occurrence). Two grammatical shapes, both requiring the ADR to be the
# verb's object — so "override files … see ADR 14" and "do NOT web-search … ADR 13" stay clean.
_ADRREF = r'ADR[- ]?0*(\d{1,4})'
CONTRA_A = re.compile(rf'(?:supersed\w*|replac\w*|revers\w*|overrid\w*)[\s:—–-]{{0,3}}{_ADRREF}', re.I)  # verb→ADR
CONTRA_B = re.compile(rf'{_ADRREF}\s+(?:is\s+|was\s+|now\s+){{0,3}}(?:supersed\w*|replaced|reversed|overridden|no\s+longer)\b', re.I)  # ADR→dead
# Skill-dir-relative (NOT project ROOT): the one-time post-install intro marker lives with the skill itself,
# so it fires on first use after an install and self-suppresses forever after — per install, not per project.
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INTRO_MARKER = os.path.join(SKILL_ROOT, '.introduced')
try:
    KEEL_VERSION = open(os.path.join(SKILL_ROOT, 'VERSION')).read().strip()
except OSError:
    KEEL_VERSION = 'unknown'


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


class _FileLock:
    """Guard for read-modify-write files (asks/escalations): lock like the whiteboard (Unix; best-effort
    on Windows). Combined with atomic replace so a crash can't leave a torn file."""
    def __init__(self, path):
        self.p = path + '.lock'
    def __enter__(self):
        _ensure(os.path.dirname(self.p))
        self.f = open(self.p, 'a')
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_EX)
        return self
    def __exit__(self, *a):
        if fcntl:
            fcntl.flock(self.f, fcntl.LOCK_UN)
        self.f.close()


def _atomic_write(path, content):
    tmp = path + '.tmp' + str(os.getpid())
    with open(tmp, 'w', encoding='utf-8') as f:
        f.write(content)
    os.replace(tmp, path)


def _append_jsonl(p, obj):
    _ensure(os.path.dirname(p))
    if p.startswith(STATE):
        _ensure_keel_ignored()
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


# ---------------- layout resolution (robust enforcement on non-canonical repos) ----------------
# keel enforces on whatever layout a repo actually uses. The anchor may be README/CLAUDE/AGENTS when there
# is no docs/architecture.md; decisions/journal may live under adr/ or docs/rfcs/. Resolution order:
# explicit `.keel/layout` override  >  first existing autodetected candidate  >  canonical default.
# On a canonical repo every slot resolves to the canonical path — so checks AND write targets are unchanged.

def _layout_override(slot):
    """`.keel/layout` holds `slot=relpath` lines; an explicit user override always wins over autodetection."""
    for line in _read(os.path.join(STATE, 'layout')).splitlines():
        if '=' in line:
            k, v = line.split('=', 1)
            if k.strip() == slot and v.strip():
                return os.path.abspath(os.path.join(ROOT, os.path.expanduser(v.strip())))
    return None


def _resolve_file(slot, default, candidates):
    return _layout_override(slot) or next((c for c in candidates if os.path.isfile(c)), default)


def _resolve_dir(slot, default, candidates):
    return _layout_override(slot) or next(
        (c for c in candidates if os.path.isdir(c) and glob.glob(os.path.join(c, '*.md'))), default)


ANCHOR = _resolve_file('anchor', ANCHOR_CANON, [
    ANCHOR_CANON, os.path.join(ROOT, 'README.md'), os.path.join(ROOT, 'CLAUDE.md'), os.path.join(ROOT, 'AGENTS.md')])
DEC = _resolve_dir('decisions', DEC_CANON, [
    DEC_CANON, os.path.join(ROOT, 'adr'), os.path.join(DOCS, 'rfcs'), os.path.join(ROOT, 'rfcs'), os.path.join(ROOT, 'ADR')])
JRN = _resolve_dir('journal', JRN_CANON, [
    JRN_CANON, os.path.join(ROOT, 'journal'), os.path.join(DOCS, 'journals')])


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
    _ensure(DOCS, DEC_CANON, JRN_CANON, MEM, STATE, CLAIMS, VERIFY_DIR,
            os.path.join(ROOT, 'archive', 'inputs'), os.path.join(ROOT, 'archive', 'scratch'))
    if not os.path.exists(DELIVERABLES):
        open(DELIVERABLES, 'w').write('data\n')  # finals live here; intermediates/scratch → archive/
    if not os.path.exists(ANCHOR_CANON):
        with open(ANCHOR_CANON, 'w') as f:
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


def _journals_sorted():
    """Date-prefix primary (stable across clones), mtime as same-day tiebreak — several entries on one
    day otherwise sort alphabetically and the 'newest journal' line lies."""
    return sorted(glob.glob(os.path.join(JRN, '*.md')),
                  key=lambda p: (os.path.basename(p)[:10], _mtime(p), os.path.basename(p)))


DEC_FILE_CANDS = [os.path.join(DOCS, 'DECISIONS.md'), os.path.join(ROOT, 'DECISIONS.md'), os.path.join(DOCS, 'decisions.md')]


def _dec_file():
    """A single-file decision log (docs/DECISIONS.md with '## Decision N' sections) — a very common
    convention keel used to read as '0 ADR'. Honored via explicit override, or autodetected when no
    folder ADRs exist. Read + checks only; new decisions stay one-per-file with a pointer appended."""
    ov = _layout_override('decisions')
    if ov and os.path.isfile(ov):
        return ov
    # honored UNCONDITIONALLY when present: folder ADRs and a log coexist by design (keel writes
    # one-per-file + appends a pointer), so recognition must not flip off after the first landing
    return next((c for c in DEC_FILE_CANDS if os.path.isfile(c)), None)


def _dec_entries():
    """Unified decisions view: folder ADRs + single-file-log sections → [{'num','title','text','src'}]."""
    out = []
    for p in _decisions():
        t = _read(p)
        m = re.match(r'0*(\d+)', os.path.basename(p))
        h = re.search(r'^#\s+(.+)$', t, re.M)
        out.append({'num': int(m.group(1)) if m else 0,
                    'title': (h.group(1).strip() if h else os.path.basename(p)), 'text': t, 'src': p})
    df = _dec_file()
    if df:
        raw = _read(df)
        heads = list(re.finditer(r'^#{1,3}\s*(?:Decision\s*)?#?0*(\d+)\s*[—:.\-]?\s*(.*)$', raw, re.M))
        for i, m in enumerate(heads):
            end = heads[i + 1].start() if i + 1 < len(heads) else len(raw)
            out.append({'num': int(m.group(1)),
                        'title': f'{int(m.group(1)):04d} — {m.group(2).strip() or "(untitled)"}',
                        'text': raw[m.start():end], 'src': df})
    return out


def _dec_tag(text):
    if re.search(r'PARTIALLY\s+SUPERSED', text, re.I):
        return '  [PARTIALLY SUPERSEDED]'
    if re.search(r'^>\s*\*\*SUPERSED|Status:\s*supersed', text, re.I | re.M):
        return '  [SUPERSEDED]'
    return ''


def _doc_inventory():
    """Every *.md under the doc root(s) + resolved slot dirs, tagged by slot. This is what closes the
    'rehydrate only reads canonical names' gap — extra/differently-named docs are surfaced, never skipped."""
    files = set()
    for r in (DOCS, DEC, JRN):
        if os.path.isdir(r):
            files.update(os.path.abspath(p) for p in glob.glob(os.path.join(r, '**', '*.md'), recursive=True))
    # root-level docs (README/CLAUDE/AGENTS/read-first manuals) carry real rules on non-canonical repos —
    # without this shallow sweep, "nothing silently skipped" is a false promise there.
    files.update(os.path.abspath(p) for p in glob.glob(os.path.join(ROOT, '*.md')))
    if os.path.isfile(ANCHOR):
        files.add(os.path.abspath(ANCHOR))
    anch, dm = os.path.abspath(ANCHOR), os.path.abspath(os.path.join(DOCS, 'data-model.md'))
    decset = {os.path.abspath(p) for p in _decisions()}
    jrnset = {os.path.abspath(p) for p in glob.glob(os.path.join(JRN, '*.md'))}
    tagged = []
    for ap in sorted(files):
        if ap == anch: t = 'anchor'
        elif ap == dm: t = 'data-model'
        elif ap in decset: t = 'decision'
        elif ap in jrnset: t = 'journal'
        elif ap == os.path.abspath(ASKS_MD): t = 'asks'
        else: t = 'other'
        tagged.append((t, os.path.relpath(ap, ROOT) if ap.startswith(ROOT) else ap))
    return tagged


def _anchor_rot():
    """Content-level anchor rot the mtime check can't see: pointers at a different skill, machine-specific
    absolute paths outside this repo, referenced repo files that no longer exist. First ~30 lines only;
    deterministic string checks, no semantics claimed. (Observed live: an anchor instructing the wrong skill.)"""
    if not os.path.exists(ANCHOR):
        return []
    rots, head = [], '\n'.join(_read(ANCHOR).splitlines()[:30])
    for m in re.finditer(r'skills/([a-z0-9_\-]+)/', head):
        if m.group(1) != 'keel':
            rots.append(f'points at skill "{m.group(1)}" — not keel; update the rehydration pointer')
    for m in re.finditer(r'(/Users/[^\s`"\')\]]+|/home/[^\s`"\')\]]+)', head):
        p = m.group(1).rstrip('.,;:')
        if not os.path.abspath(p).startswith(ROOT):
            rots.append(f'machine-specific absolute path: {p[:60]} — breaks on any other machine/clone')
    seen = set()
    return [r for r in rots if not (r in seen or seen.add(r))][:4]


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
    entries = _dec_entries()  # folder ADRs + single-file-log sections both participate
    for tier, p in tiers:
        for line in _read(p).splitlines():
            m = CONTRA_A.search(line) or CONTRA_B.search(line)
            if m:
                n = int(m.group(1))
                target = next((e['text'] for e in entries if e['num'] == n), None)
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
  keel is installed — your disciplined partner.
======================================================================

keel helps you BUILD and EVOLVE anything complex — software (web apps, data
pipelines, automation, CLI, ML) AND goal-shaped projects (a personal brand, an
outreach push, a launch). It is not a vending machine: it maps before it writes,
clarifies before it codes, and verifies before it says "done."

BIG FUZZY GOAL? It won't dive in. It decomposes the outcome into checkpoints,
aligns each with you through plain tradeoff-choices, and tracks the shape in
docs/roadmap.md — so you get exactly what you wanted, not something unaligned.

THE LOOP
  rehydrate -> [decompose the outcome ->] [discuss <-> clarify] -> build (behind a contract) -> verify -> hydrate
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
  Just tell it what you want to build, change, or achieve. On an existing project,
  say "rehydrate" (or start describing the work) and it loads context first.
  Standing state survives sessions: a freeze stays frozen, an unanswered
  escalation stays blocking, an open ask stays open — until YOU clear them.
  (docs.py --version prints the installed version.)

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
    blocking, advisory = [], []  # (summary, fix-command) — split so exit-1 means "do not build", not "mtime moved"
    if _maybe_intro():
        print()
    print('=' * 70); print(f'KEEL REHYDRATE — digest across all tiers  (keel {KEEL_VERSION})'); print('=' * 70)
    st = _stance()
    if st:
        st['rehydrates_since'] = st.get('rehydrates_since', 0) + 1
        json.dump(st, open(STANCE, 'w'))
        print(f'\n>>> STANDING STANCE: {st["name"]} (set {st["rehydrates_since"]} rehydrate(s) ago)'
              + (' — FREEZE: blocks builds + memory landings (raw edits cannot be gated)' if st.get('freeze') else '')
              + (' — memory writes need confirmation' if st.get('memory') == 'confirm' else '')
              + (f'\n>>> note: {st["note"]}' if st.get('note') else '')
              + '\n>>> lift with: docs.py stance clear')
    esc_open = [r for r in _load_jsonl(ESCALATIONS) if r.get('status') == 'open']
    if esc_open:
        blocking.append((f'{len(esc_open)} escalation(s) BLOCKED ON USER', 'docs.py escalate resolve <id> --choice ...'))
        print(f'\n[!!] BLOCKED — {len(esc_open)} open escalation(s) awaiting the USER (do not proceed on these threads):')
        for r in esc_open[:4]:
            print(f'    #{r["id"]} [{r.get("because")}] {r.get("question", "")[:88]}')
        print('    → docs.py escalate resolve <id> --choice ...')
    disc_open = [r for r in _load_jsonl(DISCUSS) if r.get('status') == 'open']
    if disc_open:  # advisory by design: session start orients; the hard gate lives in `contract check`
        print(f'\n[~] DISCUSSION MODE — {len(disc_open)} thread(s) still being shaped (builds gate on these):')
        for r in disc_open[:4]:
            print(f'    #{r["id"]} {r.get("thread", "")[:88]}')
        print('    → converge through cascading choices, then: docs.py discuss close <id> [--choice "..."]')
    print(f'\nPROFILE: {_read(PROFILE).strip() or "(unset — run: docs.py profile <name>)"}')
    mdirs = _memory_dirs()
    print('MEMORY tiers found: ' + (', '.join((os.path.relpath(d, ROOT) if d.startswith(ROOT) else d) for d in mdirs) or '(none)'))
    _lead = _read(SESSION_MODEL).strip()  # dormant unless a lead is declared — no line for the 99% who don't
    if _lead:
        _r = _roles(_lead)
        if _r and not _r['solo']:
            print(f'LEAD: {_r["lead"]} — delegate grunt to {_r["grunt"]}, {_r["judge"]}-judge it, orchestrate here (same outcome, cheaper).')
        elif _r:
            print(f'LEAD: {_r["lead"]} (solo — no cheaper capable tier; verify your own output).')

    # OUTCOME DECOMPOSITION — no-op when docs/roadmap.md doesn't exist (every project that never runs
    # `docs.py outcome set` sees nothing here, ever). When an outcome IS set, surface where the roadmap
    # stands; ZERO checkpoints means the fuzzy outcome was never decomposed — do not let execution proceed
    # on it (mirrors `contract check` refusing a build with no signed contract).
    rm = _roadmap()
    if rm:
        _print_roadmap(rm)
        if not rm['checkpoints']:
            blocking.append((f'outcome set but NOT decomposed: "{rm["north_star"][:60]}" has 0 checkpoints',
                             'docs.py checkpoint add "<layer>"  (repeat per layer, then align each through choices)'))
            print(f'\n[!!] OUTCOME NOT DECOMPOSED — "{rm["north_star"][:70]}" has zero checkpoints.')
            print('    → a fuzzy outcome with no checkpoint-map is not ready to execute. Decompose it first:')
            print('      docs.py checkpoint add "<layer>"  (repeat per layer)   — or `docs.py outcome clear` to abandon it')
        elif not any(c['status'] == 'active' for c in rm['checkpoints']):
            advisory.append(('low', 'roadmap has no checkpoint marked active (no "you are here")', 'docs.py checkpoint status <n> active',
                             '[!] ROADMAP — no checkpoint is marked active yet (no "you are here" pointer).\n'
                             '    → docs.py checkpoint status <n> active once you know where the work currently sits.'))
        # T4 · roadmap self-contradiction: a checkpoint left `undecided` while ALREADY carrying a recorded
        # choice is the "roadmap lies live" symptom — a status update that got silently dropped (e.g. lost from
        # an && chain when an earlier command exited non-zero). Precise by construction, so no cry-wolf.
        lying = [c for c in rm['checkpoints'] if c['status'] == 'undecided' and c['choices']]
        if lying:
            ex = lying[0]
            advisory.append(('high', f'{len(lying)} checkpoint(s) undecided yet carrying a recorded choice — roadmap self-contradicts',
                             f'docs.py checkpoint status {ex["n"]} reached  (or drop the stale choice)',
                             f'[!] ROADMAP CONTRADICTS ITSELF — checkpoint #{ex["n"]} "{ex["title"][:46]}" is [ ] undecided '
                             f'yet records a choice ("{ex["choices"][0][:52]}").\n'
                             '    → a status write was likely dropped (a gate-check chained before it with && exited '
                             f'non-zero). Reconcile: docs.py checkpoint status {ex["n"]} reached — or remove the choice if wrong.'))

    if os.path.exists(ANCHOR):
        alabel = os.path.relpath(ANCHOR, ROOT) if os.path.abspath(ANCHOR).startswith(ROOT) else ANCHOR
        print(f'\n--- ANCHOR ({alabel}) ---\n' + '\n'.join(_read(ANCHOR).splitlines()[:18]))
    else:
        print('\n(no anchor — looked for docs/architecture.md, README/CLAUDE/AGENTS.md — run docs.py init)')

    inv = _doc_inventory()
    other = [rel for t, rel in inv if t == 'other']
    ndec = sum(1 for t, _ in inv if t == 'decision')
    njrn = sum(1 for t, _ in inv if t == 'journal')
    print(f'\n--- DOCS INVENTORY: {len(inv)} doc(s) — nothing silently skipped ---')
    for t, rel in inv:
        if t in ('anchor', 'data-model', 'asks'):
            print(f'   [{t}] {rel}')
    print(f'   [decisions] {ndec} · [journal] {njrn}')
    if other:
        print(f'   [other] {" · ".join(other)}   ← surfaced, read on demand')

    entries = sorted(_dec_entries(), key=lambda e: e['num'])
    logsrc = _dec_file()
    print(f'\n--- DECISIONS: {len(entries)} ADR(s)' + (f' (incl. {os.path.relpath(logsrc, ROOT)})' if logsrc else '') + ' ---')
    if len(entries) > 12:
        print(f'   (+{len(entries) - 12} older not shown — docs.py read / search)')
    for e in entries[-12:]:
        print('   ' + e['title'][:84] + _dec_tag(e['text']))

    stale = _anchor_staleness()
    if stale:
        advisory.append(('low', f'anchor {len(stale)} edit(s) behind reality', 'docs.py hydrate',
                         f'[!] ANCHOR STALE — {len(stale)} file(s) changed after the anchor: {stale[:6]}\n'
                         '    → the first thing a session reads is behind reality. Run `hydrate` to refresh it.'))

    rot = _anchor_rot()
    if rot:
        advisory.append(('low', f'anchor pointer rot: {rot[0][:64]}' + (f' (+{len(rot) - 1} more)' if len(rot) > 1 else ''),
                         'edit the anchor header — it is the first thing every session reads',
                         f'[!] ANCHOR POINTER ROT — {len(rot)} issue(s) in the anchor header:\n'
                         + '\n'.join(f'    {r_}' for r_ in rot[:3])))

    contra = _contradictions()
    if contra:
        blocking.append((f'{len(contra)} live contradiction(s) — an unmarked ADR is superseded', f'docs.py supersede {contra[0][2]} --title "..."'))
        print(f'\n[!!] CONTRADICTIONS — {len(contra)} lower-tier correction(s) supersede an unmarked ADR:')
        for tier, path, n, line in contra[:8]:
            print(f'    ADR {n}: {tier}:{path} says "{line}"')
        print(f'    → do NOT act on the stale ADR. Resolve with `docs.py supersede {contra[0][2]}` first.')

    sus = _suspect_decisions()
    if sus:
        advisory.append(('low', f'suspect decision(s) {sus} referenced as superseded but not marked', 'review + docs.py supersede if real',
                         f'[!] SUSPECT (referenced as superseded, not marked): {sus}'))

    pend = [x for x in _load_jsonl(PENDING) if not x.get('drained')]
    if pend:
        advisory.append(('low', f'{len(pend)} unflushed decision/journal item(s) from a prior session', 'docs.py hydrate',
                         f'[!] {len(pend)} UNFLUSHED item(s) from a prior session (visible debt):\n'
                         + '\n'.join(f'    {x.get("kind")}: {x.get("title", "")[:80]}' + ('  (DRAFT)' if x.get('staged') else '') for x in pend[-6:])
                         + '\n    → run `docs.py hydrate` to land/drain them.'))

    if os.path.exists(VERIFY_STAMP):
        s = json.load(open(VERIFY_STAMP))
        # T4 · a verify workflow that tracks a deliverable dir which doesn't exist has a SILENTLY INERT
        # staleness net (the hash is empty both sides, so "stale" can never fire). Only surfaces for users
        # actually running verify — never nags a project that doesn't use it.
        missing_dd = [d for d in _deliverable_dirs() if not os.path.isdir(os.path.join(ROOT, d))]
        if missing_dd:
            advisory.append(('high', f'verify tracks deliverable dir(s) {missing_dd} that do not exist — staleness net is inert',
                             'docs.py deliverables <real-output-dir>',
                             f'[!] DELIVERABLES MISCONFIGURED — verify tracks "{", ".join(missing_dd)}", which does not '
                             'exist, so "verify stale" can NEVER fire (your audit safety-net is silently off).\n'
                             '    → point it at your real output: docs.py deliverables <dir> [<dir> ...]'))
        if s.get('result') != 'pass':
            blocking.append(('last audit FAILED — deliverable is not in a passing state', 'docs.py verify run'))
            print('\n[!!] VERIFY FAILED — the last audit did not pass.')
            print('    → fix, then re-run: docs.py verify run; "done" is gated on it (`verify done`).')
        elif s.get('deliverables') != _deliverable_hash():
            advisory.append(('high', 'verify stamp stale — deliverables changed since last passing audit', 'docs.py verify run',
                             '[!] VERIFY STALE — deliverables changed since the last PASSING audit (files moved/edited).\n'
                             '    → re-run to confirm still-green: docs.py verify run'))

    hyg = _hygiene_problems()
    if hyg:
        advisory.append(('low', f'{len(hyg)} hygiene issue(s) in deliverable dirs', 'docs.py hygiene',
                         f'[!] HYGIENE — {len(hyg)} issue(s), e.g.: {hyg[0]}\n    → run `docs.py hygiene` for the full list.'))

    orph = _orphan_list()
    if orph:
        advisory.append(('high', f'{len(orph)} dangling reference(s) in the memory graph', 'docs.py orphans',
                         f'[!] ORPHANS — {len(orph)} dangling reference(s), e.g. {orph[0][0]}: {orph[0][1]}\n'
                         '    → run `docs.py orphans` for the full list.'))

    parked = []
    for rid, s in _open_runs():
        npend = len(s['pending']) if isinstance(s['pending'], list) else s['pending']
        agem = int((time.time() - s['last_ts']) // 60)
        if agem > 7 * 24 * 60:  # >7 days idle: collapse to one compact line — never silent, never noisy
            parked.append(rid); continue
        age = f'{agem // 1440}d ago' if agem >= 1440 else (f'{agem // 60}h ago' if agem >= 60 else f'{agem}m ago')
        advisory.append(('high', f'run {rid} mid-flight: {len(s["done"])}/{s["total"] or "?"} done, {npend} pending ({age})', f'docs.py run resume {rid}  (or `run close {rid}` to abandon)',
                         f'[!] RUN MID-FLIGHT — {rid} "{s["man"].get("label")}": {len(s["done"])}/{s["total"] or "?"} done, '
                         f'{npend} pending, {len(s["failed"])} failed, last mark {age}' + ('  [STALLED]' if agem >= 10 else '')
                         + f'\n    → resume where it left off: docs.py run resume {rid}   (do NOT restart from 0)'))
    if parked:
        advisory.append(('low', f'{len(parked)} run(s) parked idle >7 days: {", ".join(parked)}', 'docs.py run status <id> — then resume or close',
                         f'[!] PARKED — {len(parked)} run(s) idle >7 days: {", ".join(parked)} (resume or `run close`; never auto-deleted)'))

    for stream, n, tgt in _unreconciled_sink():
        advisory.append(('high', f'{n} captured record(s) in "{stream}" not yet merged into {tgt or "target"}', f'docs.py sink import --stream {stream}',
                         f'[!] CAPTURE INBOX — {n} record(s) in "{stream}" captured but not merged into {tgt or "target"}:\n'
                         f'    → fetched data at risk of disposal. Reconcile: docs.py sink import --stream {stream}'))

    if os.path.exists(LIVETEST) and json.load(open(LIVETEST)).get('state') == 'handed_off':
        advisory.append(('low', 'livetest HANDED OFF — awaiting the user\'s live verdict', 'docs.py livetest confirm|reject --note "..."',
                         '[!] LIVETEST — handed off to the user; `verify done` stays blocked until their verdict.'))


    coord = _coord_dir()
    if coord and os.path.exists(os.path.join(coord, 'handoffs.jsonl')):
        oh = [r for r in _load_jsonl(os.path.join(coord, 'handoffs.jsonl')) if r.get('status') == 'open']
        if oh:
            advisory.append(('low', f'{len(oh)} open cross-worktree handoff(s)', 'docs.py handoff list',
                             f'[!] HANDOFFS — {len(oh)} open across this repo\'s worktrees:\n'
                             + '\n'.join(f'    #{r_["id"]} → {r_["to"]}: {r_.get("title", "")[:70]} (from {r_.get("from_worktree")})' for r_ in oh[:4])))

    open_asks = [r for r in _load_asks() if r['status'] == 'open']
    hot_asks = [r for r in open_asks if r['raised'] >= 3]
    if hot_asks:
        advisory.append(('low', f'{len(hot_asks)} ask(s) raised 3+ times still open', 'address, or docs.py ask close <id> --evidence <path>',
                         '[!] RECURRING ASK(S) — raised 3+ times and still open:\n'
                         + '\n'.join(f'    #{r["id"]} raised {r["raised"]}x: {r["text"][:84]}' for r in sorted(hot_asks, key=lambda r: -r['raised'])[:4])))
    if open_asks:
        print(f'\n--- OPEN ASKS: {len(open_asks)} standing user ask(s) (docs/asks.md) ---')
        for r in sorted(open_asks, key=lambda r: -r['raised'])[:5]:
            print(f'    #{r["id"]} raised {r["raised"]}x: {r["text"][:84]}')

    highs = [x for x in advisory if x[0] == 'high']
    lows = [x for x in advisory if x[0] == 'low']
    show_all = getattr(a, 'full', False) or len(advisory) <= 5
    for _, _, _, stanza in highs + (lows if show_all else []):
        print('\n' + stanza)
    if lows and not show_all:
        names = ' · '.join(x[3].splitlines()[0][4:].split(' — ')[0][:26] for x in lows)
        print(f'\n[!] +{len(lows)} more advisory item(s): {names}')
        print('    → each with its fix command in CORRECTIVE ACTIONS below (full stanzas: rehydrate --full)')

    js = _journals_sorted()
    print(f'\n--- newest journal --- ' + (os.path.basename(js[-1]) if js else '(none)'))
    if blocking or advisory:
        print('\n--- CORRECTIVE ACTIONS (' + f'{len(blocking)} blocking · {len(advisory)} advisory) ---')
        for i, (msg, fix) in enumerate(blocking, 1):
            print(f'  [B{i}] {msg}\n       → {fix}')
        for i, (_, msg, fix, _s) in enumerate(highs + lows, 1):
            print(f'  [A{i}] {msg}\n       → {fix}')
    print('\n' + '=' * 70)
    if blocking:
        print(f'VERDICT: ⛔ {len(blocking)} BLOCKING issue(s) — do not build on this state.'
              + (f' ({len(advisory)} advisory.)' if advisory else '') + ' (exit 1)'); sys.exit(1)
    if advisory:
        print(f'VERDICT: ⚠️  clean to build — {len(advisory)} advisory item(s) to tend when convenient.'); return
    print('VERDICT: ✅ clean — rehydrated.')


# ---------------- decision / journal (draft-able; feed the pending queue) ----------------

def _next_adr():
    n = 0
    for p in _decisions() + glob.glob(os.path.join(STATE, 'pending', '*.md')):
        b = os.path.basename(p)
        if re.match(r'\d{4}-\d{2}-\d{2}-', b):  # date-named journal draft, not an ADR — would poison numbering
            continue
        m = re.match(r'0*(\d+)', b)
        if m:
            n = max(n, int(m.group(1)))
    df = _dec_file()
    if df:  # numbers in a single-file decision log count toward the sequence too
        for m in re.finditer(r'^#{1,3}\s*(?:Decision\s*)?#?0*(\d+)\b', _read(df), re.M):
            n = max(n, int(m.group(1)))
    return n + 1


def _ensure_keel_ignored():
    """`.keel/` is private tool state and must never be committable — init isn't always run before the first
    state write, so any command that writes into .keel/ guarantees the ignore rule itself."""
    if os.path.isdir(os.path.join(ROOT, '.git')):
        gi = os.path.join(ROOT, '.gitignore')
        if '.keel/' not in _read(gi):
            with open(gi, 'a') as f:
                f.write('\n.keel/\n')


def _emit_record(kind, fn_name, content, target_dir, draft, title, extra=None):
    st = _stance()
    if st and st.get('memory') == 'confirm' and not draft:
        draft = True  # standing "confirm what you save" stance: memory writes auto-stage as drafts
        print(f'(stance "{st["name"]}": memory=confirm — staging as DRAFT for your approval)')
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
    fn = f'{n:04d}-{_slug(a.title)}.md'
    _emit_record('decision', fn, f'# {n:04d} — {a.title}\n\n{body}\n', DEC, a.draft, a.title, {'n': n})
    df = _dec_file()
    if df and not a.draft:  # repo keeps a single-file log: append a pointer so its history stays complete
        with open(df, 'a', encoding='utf-8') as f:
            f.write(f'\n> ADR {n:04d} — {a.title} (recorded at {os.path.relpath(os.path.join(DEC, fn), ROOT)})\n')
        print(f'decision: pointer appended to {os.path.relpath(df, ROOT)} (keel writes one-per-file; your log stays complete)')


def cmd_journal(a):
    fn = f'{_now():%Y-%m-%d}-{_slug(a.title)}.md'
    content = f'# {a.title}\n\n{a.content or (a.from_file and _read(a.from_file)) or ""}\n\nfriction: {a.friction or "(none)"}\n'
    _emit_record('journal', fn, content, JRN, a.draft, a.title)


def cmd_supersede(a):
    old = next((p for p in _decisions() if re.match(rf'0*{a.number}\b', os.path.basename(p))), None)
    if not old:
        sys.exit(f'no ADR {a.number} found')
    n = _next_adr()
    body = a.content or (a.from_file and _read(a.from_file)) or f'## Context\nSupersedes ADR {int(a.number):04d}.\n\n## Decision\n\n## Rejected\n'
    fn = f'{n:04d}-{_slug(a.title)}.md'
    st = _stance()
    draft = getattr(a, 'draft', False) or bool(st and st.get('memory') == 'confirm')
    # the superseding ADR goes through the same stage→approve path as every other memory write;
    # when drafted, the OLD ADR's marking is deferred to hydrate (mark_on_land) so nothing durable moves early
    _emit_record('decision', fn, f'# {n:04d} — {a.title}\n\n> Supersedes ADR {int(a.number):04d}.\n\n{body}\n',
                 DEC, draft, a.title, {'n': n, 'supersedes': int(a.number), 'mark_on_land': old})
    t = _read(old)
    already = bool(re.search(r'supersed', t, re.I))
    if draft:
        print(f'supersede: STAGED — ADR {int(a.number):04d} will be marked superseded when the draft lands (hydrate).')
    elif already:
        print(f'supersede: ADR {int(a.number):04d} was ALREADY marked — skipped re-marking; wrote superseding {fn}.')
    else:
        open(old, 'w').write('> **SUPERSEDED — see the newer ADR.**\n\n' + t)
        print(f'supersede: marked ADR {int(a.number):04d}, wrote superseding {os.path.relpath(os.path.join(DEC, fn), ROOT)}')


# ---------------- hydrate (OUTBOUND — lands approved drafts, drains queue) ----------------

def cmd_hydrate(a):
    st = _stance()
    if st and st.get('freeze'):
        staged = [x for x in _load_jsonl(PENDING) if not x.get('drained') and x.get('staged')]
        sys.exit(f'hydrate: FROZEN — stance "{st["name"]}" blocks landing into docs/. '
                 f'{len(staged)} draft(s) staged and safe; `docs.py stance clear` first, then hydrate.')
    pend = _load_jsonl(PENDING)
    live = [x for x in pend if not x.get('drained')]
    landed = 0
    for x in live:
        st_, tgt = x.get('staged'), x.get('target')
        if st_ and tgt and os.path.exists(st_):
            _ensure(os.path.dirname(tgt)); os.rename(st_, tgt); landed += 1
            mo = x.get('mark_on_land')  # a drafted supersede marks its old ADR only now, at landing
            if mo and os.path.exists(mo):
                t = _read(mo)
                if not re.search(r'supersed', t, re.I):
                    open(mo, 'w').write('> **SUPERSEDED — see the newer ADR.**\n\n' + t)
                    print(f'   marked {os.path.relpath(mo, ROOT)} superseded (deferred from draft).')
            if x.get('kind') == 'decision' and x.get('n') is not None:
                df = _dec_file()  # drafted decisions append their file-log pointer at LANDING, not staging
                if df:
                    with open(df, 'a', encoding='utf-8') as f:
                        f.write(f'\n> ADR {x["n"]:04d} — {x.get("title", "")} (recorded at {os.path.relpath(tgt, ROOT)})\n')
                    print(f'   pointer appended to {os.path.relpath(df, ROOT)} (your log stays complete)')
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
        st = _stance()
        if st and st.get('freeze'):
            print(f'contract check: ✗ FROZEN — standing stance "{st["name"]}" blocks ALL builds (even lightweight lane).'
                  f'\n  note: {st.get("note") or "(none)"}   lift with: docs.py stance clear'); sys.exit(1)
        esc_open = [r for r in _load_jsonl(ESCALATIONS) if r.get('status') == 'open']
        if esc_open:
            print(f'contract check: ✗ BLOCKED-ON-USER — {len(esc_open)} open escalation(s) (#'
                  + ', #'.join(str(r["id"]) for r in esc_open[:4]) + '). Resolve before building.'); sys.exit(1)
        disc_open = [r for r in _load_jsonl(DISCUSS) if r.get('status') == 'open']
        if disc_open:  # T1 teeth: shaping-in-progress gates the BUILD moment, and only the build moment
            print(f'contract check: ✗ DISCUSSION OPEN — {len(disc_open)} thread(s) still being shaped (#'
                  + ', #'.join(str(r["id"]) for r in disc_open[:4])
                  + '). Converge each with the user, then: docs.py discuss close <id> [--choice "..."]'); sys.exit(1)
        rm = _roadmap()  # the teeth: a declared outcome with no checkpoint-map cannot be built into directly
        if rm and rm.get('north_star') and not rm.get('checkpoints'):
            print(f'contract check: ✗ OUTCOME NOT DECOMPOSED — "{rm["north_star"][:60]}" has 0 checkpoints. '
                  'A fuzzy outcome must be broken into aligned checkpoints before any build.'
                  '\n  → docs.py checkpoint add "<layer>"  (per layer, align each through choices)'); sys.exit(1)
        if not os.path.exists(CONTRACT):
            print('contract check: NONE — no build without a signed contract.'); sys.exit(1)
        c = json.load(open(CONTRACT))
        fresh = (time.time() - c.get('ts', 0)) < (a.window or 3600)
        if c.get('approved') and fresh:
            print('contract check: ✅ signed + fresh.')
            _routing_note(c.get('plan', ''))  # model-facing cost hint; never blocks the build
            return
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
# --- PROVENANCE (tabular): every row carries source + timestamp; missing/stale rows FAIL. ---
# REQUIRE = ("source", "fetched_at"); FRESH_DAYS = 30   # adapt column names per project
# import datetime
# for i, r in enumerate(rows, 2):
#   if any(not (r.get(c) or "").strip() for c in REQUIRE): fails.append(f"row {i}: missing provenance")
#   else:
#     try:
#       age = (datetime.datetime.now() - datetime.datetime.fromisoformat(r["fetched_at"][:19])).days
#       if age > FRESH_DAYS: fails.append(f"row {i}: stale ({age}d)")
#     except ValueError: fails.append(f"row {i}: unparseable fetched_at")
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
        _lt = json.load(open(LIVETEST)).get('state') if os.path.exists(LIVETEST) else None
        if _lt == 'handed_off':
            print('verify done: ✗ HANDED OFF for the user\'s live test — self-certification is banned; '
                  'await `livetest confirm` or `livetest reject`.'); sys.exit(1)
        if _lt == 'rejected':  # the user live-tested it and said it's broken — "done" cannot pass a rejection
            print('verify done: ✗ live test REJECTED by the user — this is NOT done. Fix the deliverable, '
                  'then `livetest arm` again and earn a fresh `livetest confirm`.'); sys.exit(1)
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
    # .keel growth report — keel reports, the USER deletes (never auto-pruned, per the parked-runs ruling)
    if os.path.isdir(STATE):
        sz = sum(os.path.getsize(os.path.join(d, f)) for d, _, fs in os.walk(STATE) for f in fs)
        closed = [os.path.basename(p)[:-6] for p in glob.glob(os.path.join(RUNS, '*.jsonl'))
                  if (_run_state(os.path.basename(p)[:-6]) or {}).get('closed')]
        drained = []
        for p in glob.glob(os.path.join(INBOX, '*.jsonl')):
            stream = os.path.basename(p)[:-6]
            rec = set(_read(os.path.join(INBOX, stream + '.reconciled')).split())
            if rec and all(r.get('hash') in rec for r in _load_jsonl(p)):
                drained.append(stream)
        print(f'.keel state: {sz / 1e6:.1f} MB')
        if closed:
            print(f'  {len(closed)} closed run ledger(s) reclaimable — rm .keel/runs/<id>.jsonl for: {", ".join(closed[:6])}')
        if drained:
            print(f'  {len(drained)} fully-reconciled capture stream(s) reclaimable — rm .keel/inbox/<stream>.* for: {", ".join(drained[:6])}')
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
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_EX)
            f.write(f'{_now():%H:%M:%S} {a.by or "agent"}: {a.message}\n')
            if fcntl:
                fcntl.flock(f, fcntl.LOCK_UN)
        print('posted.')
    else:
        print(_read(WHITEBOARD) or '(whiteboard empty)')


# ---------------- profile / search / read / prefs / state / friction / clarify-depth ----------------

def cmd_profile(a):
    if a.name:
        if a.name not in PROFILES:
            sys.exit(f'profile must be one of {PROFILES}')
        prev = _read(PROFILE).strip()
        if prev and prev != a.name:  # keel tracks ONE profile — never silently swap the project's lens
            print(f'[!] replacing profile "{prev}" → "{a.name}" (keel tracks one profile per project; '
                  'hybrid repos: pick the one matching THIS session\'s work)')
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
    js = _journals_sorted()[-(a.journal_limit or 5):]
    for p in js:
        print(f'\n===== {os.path.relpath(p, ROOT)} =====\n' + _read(p))
    if len(glob.glob(os.path.join(JRN, '*.md'))) > len(js):
        print(f'\n(showing latest {len(js)} journal entries — use `search` for older)')
    if getattr(a, 'all', False):  # --all was a declared no-op; now it dumps the [other] docs too
        for t, rel in _doc_inventory():
            if t == 'other':
                p = os.path.join(ROOT, rel)
                print(f'\n===== {rel} [other] =====\n' + _read(p))


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


def cmd_feedback(a):
    """Log friction/wishes about keel ITSELF — cross-project corpus + per-project mirror. Local only, never sent.
    Fires when the user signals the tool missed something, should have acted differently, or a wish about keel."""
    if not getattr(a, 'note', None):
        rows = _load_jsonl(FEEDBACK_CENTRAL)
        if not rows:
            print(f'no keel-feedback yet — add via: docs.py feedback --note "..."   (log: {FEEDBACK_CENTRAL})'); return
        print(f'{len(rows)} keel-feedback entry(ies) — newest first  (central: {FEEDBACK_CENTRAL}):')
        for r in reversed(rows[-15:]):
            print(f'  [{str(r.get("ts",""))[:10]}] ({r.get("severity","-")}) {r.get("project","?")}: {r.get("note","")[:140]}'
                  + (f'  → {r["ref"]}' if r.get('ref') else ''))
        return
    rec = {'ts': _now().isoformat(), 'project': os.path.basename(ROOT.rstrip('/')) or ROOT, 'root': ROOT,
           'profile': _read(PROFILE).strip() or None, 'severity': getattr(a, 'severity', None) or 'med',
           'ref': getattr(a, 'ref', None), 'note': a.note}
    _append_jsonl(FEEDBACK_CENTRAL, rec)   # cross-project corpus to improve keel later
    _append_jsonl(FEEDBACK_LOCAL, rec)     # per-project mirror
    print(f'· logged to keel-feedback ({rec["severity"]}) — central + per-project.')


def cmd_layout(a):
    """Show the resolved layout, or record an explicit override in `.keel/layout` (slot=path)."""
    if getattr(a, 'set', None):
        if '=' not in a.set:
            sys.exit('usage: docs.py layout --set slot=path   (slot: anchor | decisions | journal)')
        _ensure(STATE)
        with open(os.path.join(STATE, 'layout'), 'a') as f:
            f.write(a.set.strip() + '\n')
        print(f'layout: recorded override "{a.set.strip()}" → .keel/layout'); return
    rel = lambda p: os.path.relpath(p, ROOT) if os.path.abspath(p).startswith(ROOT) else p
    inv = _doc_inventory()
    print('RESOLVED LAYOUT  (explicit override > autodetect > canonical):')
    print(f'  anchor    : {rel(ANCHOR)}' + ('' if os.path.exists(ANCHOR) else '   (none found)'))
    print(f'  decisions : {rel(DEC)}   ({len(_decisions())} ADR)')
    print(f'  journal   : {rel(JRN)}   ({len(glob.glob(os.path.join(JRN, "*.md")))} entries)')
    print(f'  docs seen : {len(inv)} total, {sum(1 for t, _ in inv if t == "other")} beyond the known slots')


# ---------------- THIN SLICES (dogfood prototypes): run · sink · stance · escalate · ask ----------------

RUNS = os.path.join(STATE, 'runs')
INBOX = os.path.join(STATE, 'inbox')
STANCE = os.path.join(STATE, 'stance.json')
ESCALATIONS = os.path.join(STATE, 'escalations.jsonl')
ASKS = os.path.join(STATE, 'asks.jsonl')
DISCUSS = os.path.join(STATE, 'discuss.jsonl')


def _run_state(rid):
    rows = _load_jsonl(os.path.join(RUNS, rid + '.jsonl'))
    if not rows:
        return None
    man = rows[0]
    items, closed, last_ts = {}, False, man.get('ts', 0)
    for r in rows[1:]:
        if r.get('close'):
            closed = True
        elif r.get('item'):
            items[r['item']] = r; last_ts = r.get('ts', last_ts)
    done = sorted(i for i, r in items.items() if r.get('status') == 'done')
    failed = sorted(i for i, r in items.items() if r.get('status') == 'failed')
    skip = sorted(i for i, r in items.items() if r.get('status') == 'skip')
    universe = man.get('items') or []
    total = len(universe) or man.get('count') or 0
    pending = ([i for i in universe if i not in items] if universe
               else max(0, total - len(done) - len(skip)))
    return {'man': man, 'done': done, 'failed': failed, 'skip': skip, 'pending': pending,
            'total': total, 'closed': closed, 'last_ts': last_ts}


def _open_runs():
    out = []
    for p in sorted(glob.glob(os.path.join(RUNS, '*.jsonl'))):
        rid = os.path.basename(p)[:-6]
        s = _run_state(rid)
        if not s or s['closed']:
            continue
        npend = len(s['pending']) if isinstance(s['pending'], list) else s['pending']
        if npend > 0 or s['failed']:
            out.append((rid, s))
    return out


def cmd_run(a):
    _ensure(RUNS)
    if a.action == 'start':
        rid = 'r' + _hash((a.label or 'run') + str(time.time()))[:4]
        items = None
        if a.items:  # plain file of ids, or file.csv:column — never make the user hand-build a list
            spec = a.items.split(':', 1)
            raw = _read(spec[0])
            if len(spec) == 2 and raw:
                import csv as _csv
                items = [r[spec[1]].strip() for r in _csv.DictReader(raw.splitlines()) if (r.get(spec[1]) or '').strip()]
            else:
                items = [x.strip() for x in raw.splitlines() if x.strip()]
        man = {'label': a.label or 'run', 'ts': time.time(), 'host': platform.node()}
        if items:
            man['items'] = items
        elif a.count:
            man['count'] = a.count
        _append_jsonl(os.path.join(RUNS, rid + '.jsonl'), man)
        print(f'RUN {rid} "{man["label"]}" — 0/{len(items) if items else a.count or "?"} (append-only ledger: .keel/runs/{rid}.jsonl)')
        if not items:
            print('[!] no item list — if this dies I can only say HOW MANY remain, not WHICH.')
            print('    marks with real ids (`run mark ' + rid + ' <real-id>`) make resume exact as you go;')
            print('    or start with --items <file> / --items <file.csv:column> to ingest ids from an existing artifact.')
    elif a.action == 'mark':
        if not a.run_id or not a.item:
            sys.exit('run mark <run-id> <item> [--status done|failed|skip] [--by agent]')
        _append_jsonl(os.path.join(RUNS, a.run_id + '.jsonl'),
                      {'item': a.item, 'status': a.status or 'done', 'by': a.by, 'ts': time.time()})
        print(f'run {a.run_id}: {a.item} → {a.status or "done"}' + (f' (by {a.by})' if a.by else ''))
    elif a.action in ('status', 'resume', 'close'):
        if not a.run_id:
            sys.exit(f'run {a.action} <run-id>')
        s = _run_state(a.run_id)
        if not s:
            sys.exit(f'no run {a.run_id}')
        npend = len(s['pending']) if isinstance(s['pending'], list) else s['pending']
        if a.action == 'close':
            _append_jsonl(os.path.join(RUNS, a.run_id + '.jsonl'), {'close': True, 'ts': time.time()})
            print(f'run {a.run_id} closed ({len(s["done"])} done, {npend} pending abandoned).'); return
        if a.action == 'resume':
            if isinstance(s['pending'], list):
                for i in s['pending'] + s['failed']:
                    print(i)
                print(f'# {len(s["pending"])} pending + {len(s["failed"])} failed to retry — skip-what-is-done is the resume', file=sys.stderr)
            else:
                # universe unknown — the ledger still auto-learned every marked id; emit the done-set to SKIP
                print(f'# universe unknown (started with --count): {len(s["done"])} done, ~{npend} pending', file=sys.stderr)
                print('# SKIP these already-done ids (auto-learned from marks) — everything else is fair game:', file=sys.stderr)
                for i in s['done'] + s['skip']:
                    print(i)
            return
        age = time.time() - s['last_ts']
        print(f'RUN {a.run_id} "{s["man"].get("label")}"  host={s["man"].get("host")}')
        print(f'  progress  {len(s["done"])}/{s["total"] or "?"} done · {len(s["failed"])} failed · {npend} pending')
        print(f'  last mark {int(age // 60)}m{int(age % 60)}s ago' + ('   [STALLED >10m]' if age > 600 else ''))
        by = defaultdict(int)
        for r in _load_jsonl(os.path.join(RUNS, a.run_id + '.jsonl'))[1:]:
            if r.get('item') and r.get('by'):
                by[r['by']] += 1
        if by:
            print('  by-agent  ' + ' · '.join(f'{k}:{v}' for k, v in sorted(by.items())))


def cmd_sink(a):
    _ensure(INBOX)
    if a.action == 'add':
        payload = a.data or (a.from_file and _read(a.from_file)) or ''
        if not payload.strip():
            sys.exit('sink add: needs --data or --from (the fetched payload)')
        h = _hash(payload)
        stream = os.path.join(INBOX, a.stream + '.jsonl')
        if any(r.get('hash') == h for r in _load_jsonl(stream)):
            print(f'sink: duplicate (hash {h}) — already buffered, not re-adding.'); return
        rec = {'hash': h, 'target': a.target, 'provenance': a.provenance, 'ts': time.time()}
        if len(payload) > 262144:  # soft cap: big payloads go to a blob file, ledger keeps the pointer
            _ensure(os.path.join(INBOX, 'blobs'))
            bp = os.path.join(INBOX, 'blobs', h)
            open(bp, 'w', encoding='utf-8').write(payload)
            rec['blob'] = bp
        else:
            rec['payload'] = payload
        _append_jsonl(stream, rec)
        n = len(_load_jsonl(stream))
        print(f'sink: +1 {a.stream} (hash {h}{", blob" if "blob" in rec else ""}) — {n} buffered durably'
              + (f' → {a.target}' if a.target else ''))
    elif a.action == 'status':
        for p in sorted(glob.glob(os.path.join(INBOX, '*.jsonl'))):
            stream = os.path.basename(p)[:-6]
            rows = _load_jsonl(p)
            rec = set(_read(os.path.join(INBOX, stream + '.reconciled')).split())
            unrec = [r for r in rows if r.get('hash') not in rec]
            tgt = rows[-1].get('target') if rows else '?'
            old = (time.time() - min((r['ts'] for r in unrec), default=time.time())) / 3600
            print(f'  {stream:12} → {tgt or "?"}   {len(unrec)} buffered · {len(rows) - len(unrec)} reconciled'
                  + (f' · oldest {old:.1f}h ago' if unrec else ''))
        if not glob.glob(os.path.join(INBOX, '*.jsonl')):
            print('  (no capture streams)')
    elif a.action == 'import':
        stream = os.path.join(INBOX, a.stream + '.jsonl')
        recp = os.path.join(INBOX, a.stream + '.reconciled')
        rec = set(_read(recp).split())
        rows = _load_jsonl(stream)
        new = [r for r in rows if r.get('hash') not in rec]
        merged = 0
        for r in new:
            tgt = r.get('target')
            if not tgt:
                continue
            payload = r.get('payload') or (_read(r['blob']) if r.get('blob') else '')
            tp = os.path.join(ROOT, tgt)
            _ensure(os.path.dirname(tp) or ROOT)
            with open(tp, 'a', encoding='utf-8') as f:
                f.write(payload.rstrip('\n') + '\n')
            rec.add(r['hash']); merged += 1
        open(recp, 'w').write('\n'.join(sorted(rec)))
        print(f'sink import {a.stream}: {len(rows)} buffered → {merged} new merged, {len(rows) - len(new)} already present.')
        ap = os.path.join(VERIFY_DIR, 'audit.py')
        if merged and os.path.exists(ap):  # catch what prevention missed — run the repo's own audit
            print('post-merge verify (this repo has an audit):')
            if os.system(f'"{sys.executable}" "{ap}"') != 0:
                print('[!!] post-merge audit FAILED — inspect the target before building on it.')


def _unreconciled_sink():
    out = []
    for p in sorted(glob.glob(os.path.join(INBOX, '*.jsonl'))):
        stream = os.path.basename(p)[:-6]
        rec = set(_read(os.path.join(INBOX, stream + '.reconciled')).split())
        unrec = [r for r in _load_jsonl(p) if r.get('hash') not in rec]
        if unrec:
            out.append((stream, len(unrec), unrec[-1].get('target')))
    return out


def _stance():
    try:
        return json.load(open(STANCE))
    except (OSError, ValueError):
        return None


def cmd_stance(a):
    if a.action == 'clear':
        try:
            os.remove(STANCE)
        except OSError:
            pass
        print('stance cleared — normal operation.')
        # continuous durability across the freeze boundary: surface what was staged, offer the landing
        pend = [x for x in _load_jsonl(PENDING) if not x.get('drained') and x.get('staged')]
        if pend:
            print(f'{len(pend)} draft(s) were staged during the stance and are waiting for approval:')
            for x in pend[-6:]:
                print(f'   {x.get("kind")}: {x.get("title", "")[:72]}')
            print('→ land them now: docs.py hydrate')
        return
    if a.action == 'show' or not a.name:
        s = _stance()
        print(json.dumps(s, indent=2) if s else '(no standing stance)')
        return
    _ensure(STATE); _ensure_keel_ignored()
    # two stances only (user-decided cut of named modes): freeze = hold everything durable;
    # confirm = work proceeds but memory writes stage as drafts. --note carries the user's words verbatim.
    s = {'name': a.name, 'freeze': a.name == 'freeze',
         'blocks_lightweight': a.name == 'freeze',
         'memory': 'confirm' if (a.name == 'confirm' or a.memory == 'confirm') else 'silent',
         'note': a.note or '', 'ts': time.time(), 'rehydrates_since': 0}
    json.dump(s, open(STANCE, 'w'))
    print(f'STANDING STANCE set: {a.name}' + (' — FREEZE: no builds/edits/landings until `stance clear` (staging drafts still allowed)' if s['freeze'] else '')
          + (' — memory writes require confirmation (auto-draft)' if s['memory'] == 'confirm' else ''))


def cmd_escalate(a):
    if a.action == 'raise':
        rows = _load_jsonl(ESCALATIONS)
        eid = max((r.get('id', 0) for r in rows), default=0) + 1
        _append_jsonl(ESCALATIONS, {'id': eid, 'question': a.question, 'domain': a.domain,
                                    'because': a.because or 'pivotal', 'options': a.options,
                                    'recommend': a.recommend, 'status': 'open', 'ts': time.time()})
        print(f'ESCALATION #{eid} — BLOCKED ON USER ({a.because or "pivotal"}). This thread will NOT proceed until resolved.')
        print(f'  Q: {a.question}' + (f'\n  options: {a.options}  (recommend: {a.recommend})' if a.options else ''))
    elif a.action == 'list':
        for r in _load_jsonl(ESCALATIONS):
            if r.get('status') == 'open':
                print(f'  #{r["id"]} [{r.get("because")}] {r.get("question", "")[:90]}')
    elif a.action in ('resolve', 'retract'):
        with _FileLock(ESCALATIONS):
            rows = _load_jsonl(ESCALATIONS)
            tgt = next((r for r in rows if r.get('id') == a.id and r.get('status') == 'open'), None)
            if not tgt:
                sys.exit(f'no open escalation #{a.id}')
            tgt['status'] = 'retracted' if a.action == 'retract' else 'resolved'
            tgt['choice'] = a.choice
            _atomic_write(ESCALATIONS, ''.join(json.dumps(r) + '\n' for r in rows))
        if a.action == 'resolve' and a.to_decision:
            n = _next_adr()
            body = f'## Context\nEscalation #{a.id}: {tgt.get("question")}\n\n## Decision\n{a.choice}\n\n## Rejected\n{tgt.get("options") or "(other options)"}\n'
            _emit_record('decision', f'{n:04d}-{_slug(a.to_decision)}.md', f'# {n:04d} — {a.to_decision}\n\n{body}\n',
                         DEC, False, a.to_decision, {'n': n})
        print(f'escalation #{a.id} {tgt["status"]}' + (f' → choice: {a.choice}' if a.choice else ''))


def cmd_status(a):
    """The clean, glanceable VISIBILITY panel (T8): what keel HAS and what's OPEN for this project, always
    recomputed from disk — a lie-detector, never a stored/cached number. A pure readout: it NEVER gates,
    always exits 0 (rehydrate stays the heavy session-start digest that can block). `--line` prints the
    one-line ambient form the agent surfaces on capture-turns; the full panel is on-demand / after heavy runs.
    Both are views of the SAME truth, so they can't disagree."""
    ver = KEEL_VERSION
    prof = _read(PROFILE).strip() or '(unset)'
    decs = _dec_entries()
    js = _journals_sorted()
    rm = _roadmap()
    asks_open = [x for x in _load_asks() if x['status'] == 'open']
    disc_open = [r for r in _load_jsonl(DISCUSS) if r.get('status') == 'open']
    esc_open = [r for r in _load_jsonl(ESCALATIONS) if r.get('status') == 'open']
    st = _stance()
    contract = json.load(open(CONTRACT)) if os.path.exists(CONTRACT) else None
    verify = json.load(open(VERIFY_STAMP)) if os.path.exists(VERIFY_STAMP) else None
    phases = ''
    if rm and rm.get('checkpoints'):
        tag = {'reached': 'x', 'active': '~', 'undecided': ' '}
        bar = ''.join('[' + tag.get(c['status'], ' ') + ']' for c in rm['checkpoints'])
        here = next((c for c in rm['checkpoints'] if c['status'] == 'active'), None)
        phases = bar + (f'  → you are here: #{here["n"]} {here["title"][:38]}' if here else '')

    if getattr(a, 'line', False):  # the ambient one-liner the agent surfaces when keel captured something
        bits = [f'keel {ver}']
        if decs: bits.append(f'{len(decs)} decision(s)')
        if disc_open: bits.append(f'{len(disc_open)} thread(s) open')
        if rm and rm.get('checkpoints'):
            bits.append(f'phase {sum(1 for c in rm["checkpoints"] if c["status"] == "reached")}/{len(rm["checkpoints"])}')
        if st and st.get('freeze'): bits.append('FROZEN')
        if esc_open: bits.append(f'{len(esc_open)} blocked-on-you')
        print('▸ ' + ' · '.join(bits) + '   → `keel status` for the full picture')
        return

    W = 64
    print('─' * W)
    print(f'keel status · {os.path.basename(ROOT) or "project"}')
    print(f'keel {ver} · profile: {prof}')
    print('\nIN MEMORY')
    print(f'  decisions  {len(decs):>3}' + (f'   latest: {decs[-1]["title"][:44]}' if decs else '   (none yet)'))
    print(f'  journal    {len(js):>3}' + (f'   latest: {os.path.basename(js[-1])[:44]}' if js else '   (none yet)'))
    if rm:
        print(f'  roadmap        {(rm["north_star"] or "(no north star)")[:44]}')
        if phases: print(f'                 {phases}')
    if asks_open: print(f'  asks       {len(asks_open):>3}   open question(s)')
    print('\nOPEN NOW')
    opened = False
    if disc_open:
        opened = True
        print(f'  discuss    {len(disc_open)} being shaped: ' + '; '.join(r.get('thread', '')[:32] for r in disc_open[:3]))
    if esc_open:
        opened = True
        print(f'  escalation {len(esc_open)} BLOCKED-ON-YOU (#' + ', #'.join(str(r['id']) for r in esc_open[:4]) + ')')
    if st:
        opened = True
        print(f'  stance     {st["name"]}' + (' — FREEZE: no builds/landings' if st.get('freeze') else ''))
    if contract:
        opened = True
        fresh = (time.time() - contract.get('ts', 0)) < 3600
        print(f'  contract   {"approved" if contract.get("approved") else "unapproved"}, {"fresh" if fresh else "stale"}')
    if verify:
        opened = True
        print(f'  verify     last audit: {verify.get("result", "?")}')
    if not opened:
        print('  (nothing open — clean)')
    print('\n→ full digest + any gates: docs.py rehydrate')
    print('─' * W)


def cmd_deliverables(a):
    """Show or set which dir(s) hold the FINAL deliverables that `verify` tracks for staleness (default: data/).
    Repoint when your outputs live elsewhere (a service dir, a db) so the staleness safety-net actually fires
    instead of watching an empty/absent folder — the F11 'silently inert' case."""
    if a.dirs:
        _ensure(STATE)
        open(DELIVERABLES, 'w').write('\n'.join(a.dirs) + '\n')
        missing = [d for d in a.dirs if not os.path.isdir(os.path.join(ROOT, d))]
        print(f'deliverables → {", ".join(a.dirs)} — verify staleness now tracks these.'
              + (f'\n  [!] note: {", ".join(missing)} does not exist yet.' if missing else ''))
    else:
        cur = _deliverable_dirs()
        missing = [d for d in cur if not os.path.isdir(os.path.join(ROOT, d))]
        print('deliverable dirs (verify staleness tracks these): ' + ', '.join(cur)
              + (f'\n  [!] missing (staleness inert until fixed): {", ".join(missing)}' if missing else ''))


def cmd_discuss(a):
    """Discussion Mode (T1). An OPEN thread = an outcome-shaping direction still being shaped WITH the user
    through cascading, steelmanned choices — augmentation, not automation: the goal of an option round is
    the user's clarity, not their selection, and the free text they attach to a pick is the yield, never a
    footnote. Teeth live at the BUILD moment only: `contract check` refuses while any thread is open;
    rehydrate surfaces open threads advisory-only (session start is orientation, not obstruction). Exit is
    PER-THREAD: close the converged thread, others stay open; a settled close is never re-asked.
    Honest limits: opening/closing is agent judgment (doctrine-primary detection, SKILL.md §0b), and raw
    Write/Edit/Bash bypass this like every gate — this arms the same proven plumbing as escalations."""
    if a.action == 'open':
        # --thread is repeatable (list); tolerate a bare string too so one call arms every part of a multi-part input
        threads = a.thread if isinstance(a.thread, list) else ([a.thread] if a.thread else [])
        if not threads:
            sys.exit('discuss open: needs --thread "<direction>" (repeat --thread to arm a multi-part input as a set)')
        rows = _load_jsonl(DISCUSS)
        nid = max((r.get('id', 0) for r in rows), default=0)
        for t in threads:
            nid += 1
            _append_jsonl(DISCUSS, {'id': nid, 'thread': t, 'status': 'open', 'ts': time.time()})
            print(f'DISCUSS #{nid} OPEN — "{t}".')
        print('Shaping mode: decompose each into steelmanned either/or choices, one fork at a time; harvest '
              'every attachment the user adds to an answer as its OWN thread. Builds gate until EACH converges '
              '→ docs.py discuss close <id> [--choice "..."]  (discuss list shows what is still open)')
    elif a.action == 'list':
        rows = [r for r in _load_jsonl(DISCUSS) if r.get('status') == 'open']
        if not rows:
            print('(no open discussion threads)')
        for r in rows:
            print(f'  #{r["id"]} {r.get("thread", "")[:90]}')
    elif a.action == 'close':
        if a.id is None:
            sys.exit('discuss close: needs the thread id (see: discuss list)')
        with _FileLock(DISCUSS):
            rows = _load_jsonl(DISCUSS)
            tgt = next((r for r in rows if r.get('id') == a.id and r.get('status') == 'open'), None)
            if not tgt:
                sys.exit(f'no open discussion #{a.id}')
            tgt['status'] = 'closed'; tgt['choice'] = a.choice; tgt['closed_ts'] = time.time()
            _atomic_write(DISCUSS, ''.join(json.dumps(r) + '\n' for r in rows))
        if a.to_decision:  # promote the converged choice to a durable, searchable ADR (same move as escalate)
            n = _next_adr()
            body = (f'## Context\nDiscussion #{a.id}: {tgt.get("thread")}\n\n'
                    f'## Decision\n{a.choice or "(converged in discussion)"}\n')
            _emit_record('decision', f'{n:04d}-{_slug(a.to_decision)}.md',
                         f'# {n:04d} — {a.to_decision}\n\n{body}\n', DEC, False, a.to_decision, {'n': n})
        print(f'discussion #{a.id} closed' + (f' → choice: {a.choice}' if a.choice else '')
              + ' — this thread may build. (settled: do not re-ask it)')


ASKS_MD = os.path.join(DOCS, 'asks.md')  # committed + human-editable: asks are project memory, not tool state


def _load_asks():
    out = []
    for line in _read(ASKS_MD).splitlines():
        m = re.match(r'- \[(open|closed)\] #(\d+) \(raised (\d+)x\) (.*?)(?: — evidence: (.+))?$', line)
        if m:
            out.append({'status': m.group(1), 'id': int(m.group(2)), 'raised': int(m.group(3)),
                        'text': m.group(4), 'evidence': m.group(5)})
    return out


def _save_asks(rows):
    _ensure(DOCS)
    hdr = ('# Asks — standing user asks\n\n'
           'One line per ask; hand-editable. An ask stays open until closed WITH evidence\n'
           '(`docs.py ask close <id> --evidence <path>`); repeats are tracked (`ask bump <id>`).\n\n')
    _atomic_write(ASKS_MD, hdr + '\n'.join(
        f'- [{r["status"]}] #{r["id"]} (raised {r["raised"]}x) {r["text"]}'
        + (f' — evidence: {r["evidence"]}' if r.get('evidence') else '') for r in rows) + '\n')  # atomic


# ---------------- THIN SLICES round 4 (tranche B): batch · coverage · livetest · substrate · handoff · provenance ----------------

COVERAGE_DIR = os.path.join(STATE, 'coverage')
LIVETEST = os.path.join(STATE, 'livetest.json')


def _coord_dir():
    """Cross-worktree coordination home: the git common dir is the ONE path every linked worktree shares."""
    import subprocess
    r = subprocess.run(['git', 'rev-parse', '--git-common-dir'], cwd=ROOT, capture_output=True, text=True)
    if r.returncode != 0:
        return None
    d = r.stdout.strip()
    return os.path.join(d if os.path.isabs(d) else os.path.join(ROOT, d), 'keel-coord')


def _cov_units(text):
    """Ground-truth units of an external source: numbered/bulleted points; fall back to substantial lines."""
    units = [re.sub(r'^[\s\-*\d.)]+', '', l).strip() for l in text.splitlines()
             if re.match(r'\s*(?:[-*]|\d+[.)])\s+\S', l)]
    if not units:
        units = [l.strip() for l in text.splitlines() if len(l.split()) >= 6]
    return [u for u in units if len(u.split()) >= 3 and not re.fullmatch(r'\[[^\]]*\]', u)]


_STOP = {'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'are', 'was', 'were', 'have', 'has',
         'will', 'should', 'would', 'could', 'about', 'their', 'they', 'them', 'your', 'our'}


def cmd_coverage(a):
    _ensure(COVERAGE_DIR)
    sp = os.path.join(COVERAGE_DIR, _slug(a.source) + '.json')
    if a.action == 'init':
        units = _cov_units(_read(a.source))
        if not units:
            sys.exit(f'coverage init: no extractable points in {a.source}')
        json.dump({'source': a.source, 'units': units, 'ts': time.time()}, open(sp, 'w'))
        print(f'coverage: {len(units)} ground-truth point(s) extracted from {a.source} — each must be addressed.')
    elif a.action == 'check':
        if not a.against:
            sys.exit('coverage check <source> --against <output-file>')
        if not os.path.exists(sp):
            sys.exit(f'no coverage set for {a.source} — run coverage init first')
        units = json.load(open(sp))['units']
        out_words = set(re.findall(r'[a-z0-9]{4,}', _read(a.against).lower())) - _STOP
        missed = []
        for u in units:
            uw = set(re.findall(r'[a-z0-9]{4,}', u.lower())) - _STOP
            if len(uw & out_words) < min(2, len(uw)):
                missed.append(u)
        if missed:
            print(f'[!!] COVERAGE FAIL — {len(missed)}/{len(units)} source point(s) NOT addressed in {a.against}:')
            for u in missed[:8]:
                print(f'    - {u[:90]}')
            print('    (keyword-level check — it proves absence of coverage, not quality of it) (exit 1)')
            sys.exit(1)
        print(f'coverage: ✅ all {len(units)} point(s) from {a.source} are addressed in {a.against}.')


def cmd_livetest(a):
    if a.action == 'arm':
        _ensure(STATE); _ensure_keel_ignored()
        json.dump({'state': 'handed_off', 'note': a.note or '', 'ts': time.time()}, open(LIVETEST, 'w'))
        print('livetest: HANDED OFF to the user for a live real-world test. '
              '`verify done` is BLOCKED until the user\'s verdict (self-certification banned).'
              + (f'\n  → {a.note}' if a.note else ''))
    elif a.action in ('confirm', 'reject'):
        if not os.path.exists(LIVETEST):
            sys.exit('livetest: nothing armed')
        st = json.load(open(LIVETEST))
        st.update({'state': 'confirmed' if a.action == 'confirm' else 'rejected',
                   'verdict_note': a.note or '', 'verdict_ts': time.time()})
        json.dump(st, open(LIVETEST, 'w'))
        print(f'livetest: {st["state"].upper()} by the user'
              + (f' — "{a.note}"' if a.note else '')
              + ('. done is unblocked.' if a.action == 'confirm' else '. back to work; re-arm after fixes.'))
    elif a.action == 'status':
        print(json.dumps(json.load(open(LIVETEST)), indent=2) if os.path.exists(LIVETEST) else '(no livetest state)')


def cmd_handoff(a):
    coord = _coord_dir()
    if not coord:
        sys.exit('handoff: not a git repo — the cross-worktree channel lives in the git common dir')
    hf = os.path.join(coord, 'handoffs.jsonl')
    if a.action == 'send':
        if not (a.to and a.title):
            sys.exit('handoff send --to <role> --title "..." [--body "..."] [--from <file>]')
        import subprocess
        sha = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], cwd=ROOT,
                             capture_output=True, text=True).stdout.strip()
        rows = _load_jsonl(hf)
        hid = max((r.get('id', 0) for r in rows), default=0) + 1
        _append_jsonl(hf, {'id': hid, 'to': a.to, 'title': a.title,
                           'body': a.body or (a.from_file and _read(a.from_file)) or '',
                           'from_worktree': os.path.basename(ROOT), 'sha': sha, 'status': 'open', 'ts': time.time()})
        print(f'handoff #{hid} → {a.to}  (from worktree "{os.path.basename(ROOT)}" @ {sha}) — visible from EVERY worktree of this repo.')
    elif a.action == 'list':
        rows = [r for r in _load_jsonl(hf) if a.all or r.get('status') == 'open']
        if not rows:
            print('(no open handoffs)'); return
        for r in rows:
            print(f'  #{r["id"]} [{r["status"]}] → {r["to"]}: {r["title"][:70]}  (from {r.get("from_worktree")} @ {r.get("sha")})')
    elif a.action == 'ack':
        rows = _load_jsonl(hf)
        tgt = next((r for r in rows if r.get('id') == a.id and r.get('status') == 'open'), None)
        if not tgt:
            sys.exit(f'no open handoff #{a.id}')
        tgt['status'] = 'acked'
        with open(hf, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        print(f'handoff #{a.id} acked.')


# ---------------- THIN SLICES round 3: accept · route · critique · coverage · livetest · handoff ----------------

ACCEPT_DIR = os.path.join(DOCS, 'acceptance')
ROUTING = os.path.join(DOCS, 'routing.md')
SESSION_MODEL = os.path.join(STATE, 'session_model')
CRITIQUE = os.path.join(STATE, 'critique.jsonl')


def cmd_accept(a):
    """Typed acceptance registry — the durable per-deliverable-TYPE definition-of-done, learned from real
    corrections (committed + hand-editable), so the quality bar stops living only in the user's head."""
    _ensure(ACCEPT_DIR)
    p = os.path.join(ACCEPT_DIR, _slug(a.type) + '.md')
    if a.action == 'add':
        if not a.criterion:
            sys.exit('accept add <type> --criterion "..."')
        first = not os.path.exists(p)
        with open(p, 'a', encoding='utf-8') as f:
            if first:
                f.write(f'# Acceptance — {a.type}\n\nDefinition-of-done for every "{a.type}" deliverable; '
                        'grown from real corrections. Hand-editable; one criterion per line.\n\n')
            f.write(f'- [ ] {a.criterion}\n')
        print(f'accept: criterion added → {os.path.relpath(p, ROOT)}')
    elif a.action == 'show':
        print(_read(p) or f'(no acceptance registry for "{a.type}" — accept add {a.type} --criterion "...")')
    elif a.action == 'check':
        crits = re.findall(r'^- \[.\] (.+)$', _read(p), re.M)
        if not crits:
            print(f'accept check: ✗ NO registry for type "{a.type}" — done cannot be claimed against an '
                  f'empty bar. Record the bar first: accept add {a.type} --criterion "..." (exit 1)')
            sys.exit(1)
        print(f'ACCEPT CHECK — "{a.type}" ({len(crits)} criteria, {os.path.relpath(p, ROOT)}). '
              'Walk EVERY line against the actual deliverable before claiming done:')
        for c in crits:
            print(f'   □ {c}')


# model tiers, best → cheapest (Fable/Mythos = the Claude 5 top tier, above Opus). Orchestration is
# tier-RELATIVE to whatever the user's LEAD model is — never hardcoded to one model.
MODEL_TIERS = ('fable', 'mythos', 'opus', 'sonnet', 'haiku')
DEFAULT_GRUNT = 'scrape|extract|dedupe|normalize|backfill|migrate|bulk|re-run|batch|crawl|fetch|convert|reformat|boilerplate|repetitive'


def _tier(name):
    n = (name or '').lower()
    return next((i for i, t in enumerate(MODEL_TIERS) if t in n), None)


def _roles(lead):
    """Derive the orchestration topology from the LEAD model — tier-relative, covers every case."""
    li = _tier(lead)
    if li is None:
        return None
    si, oi = MODEL_TIERS.index('sonnet'), MODEL_TIERS.index('opus')
    solo = li >= si                                          # sonnet (or lower) lead: no cheaper capable worker
    grunt = lead.lower() if solo else MODEL_TIERS[si]        # the 'sonnet' worker tier, else self
    judge = MODEL_TIERS[oi] if li < oi else lead.lower()     # opus verifies when lead is above opus; else self
    return {'lead': lead.lower(), 'grunt': grunt, 'judge': judge, 'solo': solo}


def _routing_note(plan):
    """Model-facing, non-blocking cost hint: if a lead is declared and a cheaper worker tier exists, name the
    grunt-shaped plan items to delegate. Dormant unless the user declared a lead — zero user-facing change."""
    sess = _read(SESSION_MODEL).strip()
    roles = _roles(sess) if sess else None
    if not roles or roles['solo']:
        return
    grunt = [l.strip()[:56] for l in plan.splitlines() if l.strip() and re.search(DEFAULT_GRUNT, l.lower())]
    if grunt:
        print(f'  · routing (cost): {len(grunt)} grunt-shaped item(s) — delegate to {roles["grunt"]} + '
              f'{roles["judge"]}-judge the return; keep orchestration on {roles["lead"]}. Same result, cheaper.')


def _print_topology(lead):
    r = _roles(lead)
    if not r:
        print(f'route: unknown model tier "{lead}" — known tiers best→cheapest: {" > ".join(MODEL_TIERS)}'); return r
    print(f'ORCHESTRATION TOPOLOGY (lead = {r["lead"]}):')
    print(f'  orchestrate · intelligence · verify  → {r["lead"]}  (the expensive, high-value work stays here)')
    if r['solo']:
        print(f'  grunt / research                     → {r["grunt"]} (SOLO — no cheaper capable tier; still verify your OWN output)')
    else:
        print(f'  grunt / bulk research / mechanical   → {r["grunt"]} (delegate DOWN — cheap to redo, don\'t spend {r["lead"]} on it)')
        print(f'  judge the grunt output before accept → {r["judge"]} (never rubber-stamp a worker\'s "done")')
    return r


def cmd_route(a):
    if a.action == 'set':
        if not (a.klass and a.keywords and a.model):
            sys.exit('route set <class> --keywords "kw|kw|kw" --model <name>')
        _ensure(DOCS)
        first = not os.path.exists(ROUTING)
        with open(ROUTING, 'a', encoding='utf-8') as f:
            if first:
                f.write('# Routing policy — task-class → model (codified once, never re-typed per session)\n\n')
            f.write(f'- {a.klass}: {a.keywords} -> {a.model}\n')
        print(f'route: {a.klass} ({a.keywords}) → {a.model}   [docs/routing.md]')
    elif a.action in ('model', 'lead'):
        if not a.model:
            sys.exit('route lead --model <name>  (declare the LEAD model THIS session runs as)')
        _ensure(STATE); _ensure_keel_ignored()
        open(SESSION_MODEL, 'w').write(a.model)
        print(f'lead model: {a.model}')
        _print_topology(a.model)  # derive + show the tier-relative orchestration roles
    elif a.action == 'check':
        sess = _read(SESSION_MODEL).strip()
        plan = (json.load(open(CONTRACT)).get('plan', '') if os.path.exists(CONTRACT) else '')
        rules = re.findall(r'^- (\w[\w-]*): (.+?) -> (\S+)$', _read(ROUTING), re.M)  # optional custom policy
        if not sess:
            print('route check: declare the lead model first — docs.py route lead --model <name>'); return
        if not plan:
            sys.exit('route check: needs a set contract (the plan whose items get routed).')
        roles = _roles(sess)
        flags = []
        for line in plan.splitlines():
            low = line.strip().lower()
            if not low:
                continue
            for klass, kws, model in rules:  # explicit policy wins
                if re.search(kws, low) and model.lower() != sess.lower():
                    flags.append((line.strip()[:60], klass, model)); break
            else:  # built-in tier-relative default: grunt-shaped work should go DOWN to the worker tier
                if roles and not roles['solo'] and re.search(DEFAULT_GRUNT, low):
                    flags.append((line.strip()[:60], 'grunt', roles['grunt']))
        if flags:
            print(f'ROUTE CHECK — lead "{sess}":')
            for item, klass, model in flags[:8]:
                print(f'   ✗ "{item}"  is {klass}-class → delegate to {model}, then judge its output')
            print(f'{len(flags)} item(s) belong a tier DOWN. Honest limit: keel cannot switch the harness model — '
                  'it detects + surfaces (ADVISORY — never blocks the build); delegate the flagged items and '
                  'verify their return.')
            return  # advisory by contract: surfaces loudly, exits 0 — nothing downstream may gate on this
        print(f'route check: ✅ every contract item is on the right tier for lead "{sess}".')



def cmd_critique(a):
    """The proposal-audit gate — verify's symmetric bookend, applied to the PLAN. Structural checks only
    (untested load-bearing assumptions, research grounding, rejected alternatives) — honesty about what a
    deterministic gate can and cannot judge."""
    chash = json.load(open(CONTRACT)).get('hash') if os.path.exists(CONTRACT) else None
    if a.action == 'assume':
        if not a.claim:
            sys.exit('critique assume --claim "..." [--bearing load|minor] [--status untested|tested|user-confirmed]')
        _append_jsonl(CRITIQUE, {'kind': 'assume', 'claim': a.claim, 'bearing': a.bearing or 'minor',
                                 'status': a.status or 'untested', 'contract': chash, 'ts': time.time()})
        print(f'critique: assumption logged ({a.bearing or "minor"}, {a.status or "untested"})')
    elif a.action == 'research':
        if not (a.angle and a.finding):
            sys.exit('critique research --angle "..." --finding "..." [--source <pointer>] [--gap "..."]')
        _append_jsonl(CRITIQUE, {'kind': 'research', 'angle': a.angle, 'finding': a.finding,
                                 'source': a.source or '', 'gap': a.gap or '', 'contract': chash, 'ts': time.time()})
        print('critique: research angle logged' + (' (gap surfaced)' if a.gap else ''))
    elif a.action == 'alt':
        if not (a.option and a.because):
            sys.exit('critique alt --option "..." --because "why rejected"')
        _append_jsonl(CRITIQUE, {'kind': 'alt', 'option': a.option, 'because': a.because,
                                 'contract': chash, 'ts': time.time()})
        print('critique: rejected alternative logged')
    elif a.action == 'check':
        rows = [r for r in _load_jsonl(CRITIQUE) if r.get('contract') == chash]
        if not chash:
            sys.exit('critique check: no contract set — the critique binds to a specific plan')
        latest = {}  # latest-per-claim wins: re-asserting an assumption with a new status supersedes the old
        for r in rows:
            if r.get('kind') == 'assume':
                latest[r.get('claim')] = r
        untested = [r for r in latest.values() if r.get('bearing') == 'load' and r.get('status') == 'untested']
        research = [r for r in rows if r.get('kind') == 'research']
        alts = [r for r in rows if r.get('kind') == 'alt']
        fails = []
        if untested:
            fails.append(f'{len(untested)} LOAD-BEARING assumption(s) untested: '
                         + '; '.join(r['claim'][:48] for r in untested[:3]))
        if not research:
            fails.append('no research angles logged — the plan cites nothing gathered')
        if not alts:
            fails.append('no rejected alternatives — a plan with no alternatives was not compared to anything')
        if fails:
            print(f'CRITIQUE CHECK — contract {chash}: ✗ NOT ready to approve:')
            for f_ in fails:
                print(f'   ✗ {f_}')
            print('(structural gate only — it verifies the plan was stress-tested, not that it is right) (exit 1)')
            sys.exit(1)
        print(f'critique check: ✅ contract {chash} — {len(rows)} ledger entries; assumptions tested, '
              f'{len(research)} research angle(s), {len(alts)} alternative(s) weighed.')


# ---------------- THIN SLICES round 2: verify-baseline · preserve · orphans · smoke ----------------

PRESERVE_DIR = os.path.join(STATE, 'preserve')
SMOKE = os.path.join(STATE, 'smoke.json')


def _units(text):
    """Preservation units — the non-trivial content a regeneration tends to silently drop:
    headings, list items, and links/citations."""
    us = set()
    for line in text.splitlines():
        s = line.strip()
        if re.match(r'#{1,6}\s+\S', s):
            us.add('H: ' + s.lstrip('#').strip()[:80])
        elif re.match(r'[-*]\s+\S', s):
            us.add('L: ' + s.lstrip('-* ').strip()[:80])
    for m in re.finditer(r'https?://[^\s)\]">]+', text):
        us.add('U: ' + m.group(0)[:80])
    return us


def cmd_preserve(a):
    _ensure(PRESERVE_DIR)
    sp = os.path.join(PRESERVE_DIR, _slug(a.file) + '.json')
    if a.action == 'snapshot':
        us = _units(_read(a.file))
        json.dump({'file': a.file, 'ts': time.time(), 'units': sorted(us)}, open(sp, 'w'))
        print(f'preserve: snapshot {a.file} — {len(us)} unit(s) (headings / list items / links).')
    elif a.action == 'check':
        if not os.path.exists(sp):
            sys.exit(f'no snapshot for {a.file} — run `preserve snapshot {a.file}` before editing')
        old = set(json.load(open(sp))['units'])
        new = _units(_read(a.file))
        lost = sorted(old - new)
        if lost:
            print(f'[!!] PRESERVE FAIL — {len(lost)}/{len(old)} snapshot unit(s) GONE from {a.file} '
                  '(regenerated instead of edited?):')
            for u in lost[:8]:
                print(f'    - {u}')
            print(f'    ({len(new - old)} new unit(s) added.) Restore the losses or justify each. (exit 1)')
            sys.exit(1)
        print(f'preserve: OK — all {len(old)} snapshot unit(s) still present ({len(new - old)} added).')


def _orphan_list():
    """Graph integrity across the memory tiers: ADR references to decisions that don't exist,
    dead relative markdown links, and [[wiki-links]] with no matching doc."""
    nums = {e['num'] for e in _dec_entries()}
    scan = glob.glob(os.path.join(DOCS, '**', '*.md'), recursive=True) + _memory_files()
    stems = {os.path.splitext(os.path.basename(p))[0].lower() for p in scan}
    dangling = []
    for p in scan:
        rel = os.path.relpath(p, ROOT) if p.startswith(ROOT) else p
        text = _read(p)
        for m in re.finditer(r'\bADR[- ]?0*(\d{1,4})\b', text):
            if int(m.group(1)) not in nums:
                dangling.append((rel, f'ADR {m.group(1)} — no such decision recorded'))
        for m in re.finditer(r'\]\((?!https?://|#|mailto:)([^)#\s]+\.md)\)', text):
            tgt = os.path.normpath(os.path.join(os.path.dirname(p), m.group(1)))
            if not os.path.exists(tgt):
                dangling.append((rel, f'link → {m.group(1)} (file missing)'))
        for m in re.finditer(r'\[\[([^\]|#]+)', text):
            if m.group(1).strip().lower() not in stems:
                dangling.append((rel, f'[[{m.group(1).strip()}]] — no doc with that name yet'))
    return dangling


def cmd_orphans(a):
    dangling = _orphan_list()
    if not dangling:
        print('orphans: none — every reference in the memory graph resolves.'); return
    print(f'orphans: {len(dangling)} dangling reference(s) across the memory graph:')
    for rel, msg in dangling[:12]:
        print(f'   {rel}: {msg}')
    if len(dangling) > 12:
        print(f'   (+{len(dangling) - 12} more)')


def cmd_smoke(a):
    if a.action == 'set':
        if not a.cmd:
            sys.exit('smoke set --cmd "<tiny end-to-end sample command>"')
        _ensure(STATE); _ensure_keel_ignored()
        json.dump({'cmd': a.cmd}, open(SMOKE, 'w'))
        print(f'smoke: gate command set: {a.cmd}')
    elif a.action == 'run':
        if not os.path.exists(SMOKE):
            sys.exit('no smoke command — `smoke set --cmd "..."` first')
        cfg = json.load(open(SMOKE))
        rc = os.system(cfg['cmd'])
        cfg.update({'last_rc': rc, 'last_ts': time.time()})
        json.dump(cfg, open(SMOKE, 'w'))
        print(f'smoke: {"PASS ✅" if rc == 0 else f"FAIL (rc {rc})"} — gate {"open" if rc == 0 else "closed"}.')
        sys.exit(1 if rc else 0)
    elif a.action == 'gate':
        cfg = json.load(open(SMOKE)) if os.path.exists(SMOKE) else None
        fresh = cfg and cfg.get('last_rc') == 0 and (time.time() - cfg.get('last_ts', 0)) < 3600
        if fresh:
            print('smoke gate: ✅ fresh passing sample run — go for the expensive run.'); return
        print('smoke gate: ✗ no fresh PASSING smoke run — validate the pipeline on a tiny sample first '
              '(`docs.py smoke run`). (exit 1)')
        sys.exit(1)


def _stem(w):
    """Naive suffix-fold so plural/verb-form variants still match (profiles→profile, composition→composit);
    min-4-char stem guards against overstemming short words."""
    for suf in ('ings', 'ing', 'ions', 'ion', 'es', 'ed', 's'):
        if w.endswith(suf) and len(w) - len(suf) >= 4:
            return w[:-len(suf)]
    return w


def cmd_match(a):
    """'Is this already decided?' — deterministic recall across ALL recorded decisions (folder + file-log),
    run at orient on the incoming ask so keel says 'settled in ADR 0015' BEFORE planning a rebuild."""
    stop = {'the', 'and', 'for', 'with', 'that', 'this', 'from', 'into', 'are', 'was', 'were', 'have', 'has'}

    def toks(s):
        return {_stem(w) for w in re.findall(r'[a-z0-9]{3,}', s.lower())} - stop

    def hit(qt, words):  # prefix-aware: 'compos(e)' matches 'composit(ion)' — stems of the same root
        return any(qt == w or (len(qt) >= 5 and w.startswith(qt)) or (len(w) >= 5 and qt.startswith(w))
                   for w in words)
    q = toks(a.query)
    scored = []
    for e in _dec_entries():
        tw, bw = toks(e['title']), toks(e['text'][:600])
        ov = sum(1 for qt in q if hit(qt, bw)) + sum(1 for qt in q if hit(qt, tw))  # title hits count double
        if ov >= 2:
            scored.append((ov, e))
    if not scored:
        print(f'match: nothing recorded resembles "{a.query[:70]}" — likely new ground.'); return
    scored.sort(key=lambda x: -x[0])
    print(f'match: closest recorded decision(s) to "{a.query[:70]}":')
    for ov, e in scored[:3]:
        print(f'   {e["title"][:80]}{_dec_tag(e["text"])}   (overlap {ov})')
    print('→ if the top hit already settles this ask, SAY SO before planning — re-run vs new work is the user\'s call.')


def cmd_ask(a):
    if a.action == 'list':
        for r in _load_asks():
            if r['status'] == 'open' or a.all:
                print(f'  #{r["id"]} [{r["status"]}] raised {r["raised"]}x: {r["text"][:90]}')
        return
    lock = _FileLock(ASKS_MD)
    lock.__enter__()
    rows = _load_asks()
    if a.action == 'add':
        aid = max((r['id'] for r in rows), default=0) + 1
        rows.append({'status': 'open', 'id': aid, 'raised': 1, 'text': a.text, 'evidence': None})
        _save_asks(rows)
        print(f'ask #{aid} recorded → docs/asks.md (committed, hand-editable) — open until closed with --evidence.')
    elif a.action == 'bump':
        tgt = next((r for r in rows if r['id'] == a.id), None)
        if not tgt:
            sys.exit(f'no ask #{a.id}')
        tgt['raised'] += 1
        _save_asks(rows)
        print(f'ask #{a.id} raised {tgt["raised"]}x now — recurring asks get loud at 3+.')
    elif a.action == 'close':
        if not a.evidence:
            sys.exit('[!] ask close REJECTED — no --evidence. "resolved" without proof is a claim, not a fact. (exit 1)')
        tgt = next((r for r in rows if r['id'] == a.id and r['status'] == 'open'), None)
        if not tgt:
            sys.exit(f'no open ask #{a.id}')
        tgt['status'] = 'closed'; tgt['evidence'] = a.evidence
        _save_asks(rows)
        warn = '' if os.path.exists(os.path.join(ROOT, a.evidence)) else '   [!] evidence path not found on disk'
        print(f'ask #{a.id} closed → evidence: {a.evidence}{warn}')
    lock.__exit__()


# ---------------- OUTCOME DECOMPOSITION (dogfood prototype): outcome · checkpoint ----------------
# Closes a proven gap: a fuzzy OUTCOME ("build my personal brand on social media") got executed directly
# instead of decomposed into checkpoints and aligned through questions, one layer at a time. docs/roadmap.md
# is committed + hand-editable (same tier as docs/asks.md) — the north-star outcome, its ordered checkpoints
# (the layers), each checkpoint's status, and the choices that shaped it. `rehydrate` surfaces it read-only
# and is a strict no-op for any project that never runs `outcome set` (no roadmap.md → nothing printed, no
# new blocking/advisory entries — see the guard at the top of the inserted rehydrate block).

ROADMAP_MD = os.path.join(DOCS, 'roadmap.md')
CP_LINE = re.compile(r'^(\d+)\.\s*\[(reached|active|undecided)\]\s*(.+)$', re.M)
ROADMAP_HDR = (
    '# Roadmap — outcome decomposition\n\n'
    'A fuzzy outcome, decomposed into ordered checkpoints (the layers); each checkpoint carries a\n'
    'status (undecided | active | reached) and the choices that shaped it. Hand-editable.\n'
    '  add a checkpoint : docs.py checkpoint add "<layer>"\n'
    '  set status       : docs.py checkpoint status <n> reached|active|undecided\n'
    '  record a choice  : docs.py checkpoint choice <n> --text "..."\n\n')
ROADMAP_PLACEHOLDER = '## Checkpoints\n(none yet — docs.py checkpoint add "<layer>")\n'


def _roadmap():
    """Read docs/roadmap.md → {'north_star', 'checkpoints':[{'n','status','title','choices'}]}, or None if
    no outcome has been set — the no-op case every pre-existing project stays in forever unless it opts in."""
    if not os.path.exists(ROADMAP_MD):
        return None
    text = _read(ROADMAP_MD)
    m = re.search(r'^## North star\n(.*?)(?=\n##|\Z)', text, re.S | re.M)
    north = m.group(1).strip() if m else ''
    matches = list(CP_LINE.finditer(text))
    cps = []
    for i, cm in enumerate(matches):
        start, end = cm.end(), (matches[i + 1].start() if i + 1 < len(matches) else len(text))
        choices = [l.strip()[2:].strip() for l in text[start:end].splitlines() if l.strip().startswith('- ')]
        cps.append({'n': int(cm.group(1)), 'status': cm.group(2), 'title': cm.group(3).strip(), 'choices': choices})
    if not north and not cps:
        return None
    return {'north_star': north, 'checkpoints': cps}


def _print_roadmap(rm):
    print(f'\n--- ROADMAP: {rm["north_star"] or "(north star not set)"} ---')
    if not rm['checkpoints']:
        print('   (0 checkpoints — outcome not yet decomposed: docs.py checkpoint add "<layer>")')
        return
    active = next((c for c in rm['checkpoints'] if c['status'] == 'active'), None)
    nxt = next((c for c in rm['checkpoints'] if c['status'] == 'undecided'), None)
    tag = {'reached': '[x]', 'active': '[~]', 'undecided': '[ ]'}
    for c in rm['checkpoints']:
        here = '   <- YOU ARE HERE' if active and c['n'] == active['n'] else ''
        print(f'   {tag.get(c["status"], "[ ]")} {c["n"]}. {c["title"]}{here}')
        for ch in c['choices']:
            print(f'         choice: {ch[:90]}')
    if nxt:
        print(f'   → next undecided checkpoint: #{nxt["n"]} {nxt["title"]} — align it through questions before building on it')


def cmd_outcome(a):
    if a.action == 'clear':  # escape hatch: an outcome-set-but-undecomposed blocks; this releases it
        if not os.path.exists(ROADMAP_MD):
            print('(no outcome to clear)'); return
        os.makedirs(os.path.join(ROOT, 'archive'), exist_ok=True)
        dst = os.path.join(ROOT, 'archive', 'roadmap-cleared.md')
        os.replace(ROADMAP_MD, dst)  # archived, not destroyed — the decomposition isn't lost
        print(f'outcome: cleared — roadmap archived to {os.path.relpath(dst, ROOT)} (the block is lifted).')
        return
    if a.action == 'set':
        if not a.text or not a.text.strip():
            sys.exit('outcome set "<north star>"')
        _ensure(DOCS)
        old = _read(ROADMAP_MD)
        cm = re.search(r'(## Checkpoints\n.*)\Z', old, re.S)
        cps_block = cm.group(1) if cm else ROADMAP_PLACEHOLDER
        _atomic_write(ROADMAP_MD, ROADMAP_HDR + f'## North star\n{a.text.strip()}\n\n' + cps_block)
        print(f'outcome: north star set → {os.path.relpath(ROADMAP_MD, ROOT)}')
        if not cm:
            print('  → not a scoped task; decompose it before executing: docs.py checkpoint add "<layer>" (repeat per layer)')
    else:
        rm = _roadmap()
        if not rm:
            print('(no outcome set — docs.py outcome set "<north star>")'); return
        _print_roadmap(rm)


def cmd_checkpoint(a):
    if not os.path.exists(ROADMAP_MD):
        sys.exit('no outcome set yet — docs.py outcome set "<north star>" first')
    if a.action == 'list':
        rm = _roadmap()
        _print_roadmap(rm) if rm else print('(empty roadmap)')
        return
    rm = _roadmap() or {'north_star': '', 'checkpoints': []}
    if a.action == 'add':
        if not a.arg1 or not a.arg1.strip():
            sys.exit('checkpoint add "<layer>"')
        n = max((c['n'] for c in rm['checkpoints']), default=0) + 1
        text = _read(ROADMAP_MD).replace(ROADMAP_PLACEHOLDER, '## Checkpoints\n')
        if not text.endswith('\n'):
            text += '\n'
        text += f'{n}. [undecided] {a.arg1.strip()}\n'
        _atomic_write(ROADMAP_MD, text)
        print(f'checkpoint {n} added [undecided]: "{a.arg1.strip()}" → {os.path.relpath(ROADMAP_MD, ROOT)}')
    elif a.action == 'status':
        n, status = a.arg1, a.arg2
        if status not in ('reached', 'active', 'undecided'):
            sys.exit('checkpoint status <n> reached|active|undecided')
        text = _read(ROADMAP_MD)
        new_text, count = re.subn(rf'^{re.escape(str(n))}\.\s*\[\w+\]', f'{n}. [{status}]', text, flags=re.M)
        if not count:
            sys.exit(f'no checkpoint {n}')
        _atomic_write(ROADMAP_MD, new_text)
        print(f'checkpoint {n}: status → {status}')
    elif a.action == 'choice':
        n, txt = a.arg1, a.text
        if not n or not txt:
            sys.exit('checkpoint choice <n> --text "..."')
        lines = _read(ROADMAP_MD).splitlines(keepends=True)
        head_re = re.compile(rf'^{re.escape(str(n))}\.\s*\[\w+\]')
        out, i, inserted = [], 0, False
        while i < len(lines):
            out.append(lines[i])
            if head_re.match(lines[i]):
                j = i + 1
                while j < len(lines) and lines[j].strip().startswith('- '):
                    out.append(lines[j]); j += 1
                out.append(f'   - {txt.strip()}\n')
                i = j; inserted = True
                continue
            i += 1
        if not inserted:
            sys.exit(f'no checkpoint {n}')
        _atomic_write(ROADMAP_MD, ''.join(out))
        print(f'checkpoint {n}: choice recorded.')
        if getattr(a, 'to_decision', None):  # promote a pivotal shaping choice to a real, searchable ADR
            num = _next_adr()
            title = next((c['title'] for c in rm['checkpoints'] if c['n'] == int(n)), f'checkpoint {n}')
            body = f'## Context\nShapes checkpoint {n} ({title}) of outcome: {rm.get("north_star", "")}.\n\n## Decision\n{txt.strip()}\n\n## Rejected\n(alternatives weighed at this checkpoint)\n'
            _emit_record('decision', f'{num:04d}-{_slug(a.to_decision)}.md',
                         f'# {num:04d} — {a.to_decision}\n\n{body}\n', DEC, False, a.to_decision, {'n': num})
            print(f'   promoted to ADR {num:04d} — now searchable via docs.py match / search.')


def main():
    ap = argparse.ArgumentParser(prog='docs.py', description='keel memory + enforcement CLI')
    ap.add_argument('--version', action='version', version=f'keel {KEEL_VERSION}')
    sub = ap.add_subparsers(dest='cmd', required=True)
    for name in ('init', 'hydrate', 'contradictions', 'friction'):
        sub.add_parser(name).set_defaults(fn=globals()[f'cmd_{name}'])
    p = sub.add_parser('rehydrate'); p.add_argument('--full', action='store_true'); p.set_defaults(fn=cmd_rehydrate)
    p = sub.add_parser('intro'); p.add_argument('--force', action='store_true'); p.set_defaults(fn=cmd_intro)
    p = sub.add_parser('profile'); p.add_argument('name', nargs='?'); p.set_defaults(fn=cmd_profile)
    for name in ('decision', 'journal'):
        p = sub.add_parser(name); p.add_argument('--title', required=True); p.add_argument('--content')
        p.add_argument('--from', dest='from_file'); p.add_argument('--draft', action='store_true')
        p.set_defaults(fn=globals()[f'cmd_{name}'])
        if name == 'journal':
            p.add_argument('--friction')
    p = sub.add_parser('supersede'); p.add_argument('number', type=int); p.add_argument('--title', required=True)
    p.add_argument('--content'); p.add_argument('--from', dest='from_file'); p.add_argument('--draft', action='store_true')
    p.set_defaults(fn=cmd_supersede)
    p = sub.add_parser('contract'); p.add_argument('action', choices=['set', 'approve', 'check'])
    p.add_argument('--content'); p.add_argument('--from', dest='from_file'); p.add_argument('--approved', action='store_true')
    p.add_argument('--window', type=int); p.set_defaults(fn=cmd_contract)
    p = sub.add_parser('verify'); p.add_argument('action', choices=['init', 'run', 'done', 'sync']); p.set_defaults(fn=cmd_verify)
    p = sub.add_parser('coverage'); p.add_argument('action', choices=['init', 'check']); p.add_argument('source')
    p.add_argument('--against'); p.set_defaults(fn=cmd_coverage)
    p = sub.add_parser('livetest'); p.add_argument('action', choices=['arm', 'confirm', 'reject', 'status'])
    p.add_argument('--note'); p.set_defaults(fn=cmd_livetest)
    p = sub.add_parser('handoff'); p.add_argument('action', choices=['send', 'list', 'ack'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--to'); p.add_argument('--title'); p.add_argument('--body')
    p.add_argument('--from', dest='from_file'); p.add_argument('--all', action='store_true'); p.set_defaults(fn=cmd_handoff)
    p = sub.add_parser('preserve'); p.add_argument('action', choices=['snapshot', 'check']); p.add_argument('file'); p.set_defaults(fn=cmd_preserve)
    sub.add_parser('orphans').set_defaults(fn=cmd_orphans)
    p = sub.add_parser('smoke'); p.add_argument('action', choices=['set', 'run', 'gate']); p.add_argument('--cmd'); p.set_defaults(fn=cmd_smoke)
    sub.add_parser('hygiene').set_defaults(fn=cmd_hygiene)
    p = sub.add_parser('clarify-depth'); p.add_argument('level', nargs='?', choices=['thorough', 'light']); p.set_defaults(fn=cmd_clarify)
    p = sub.add_parser('feedback'); p.add_argument('--note'); p.add_argument('--severity', choices=['low', 'med', 'high']); p.add_argument('--ref'); p.set_defaults(fn=cmd_feedback)
    p = sub.add_parser('layout'); p.add_argument('--set'); p.add_argument('--detect', action='store_true'); p.set_defaults(fn=cmd_layout)
    p = sub.add_parser('run'); p.add_argument('action', choices=['start', 'mark', 'status', 'resume', 'close'])
    p.add_argument('run_id', nargs='?'); p.add_argument('item', nargs='?'); p.add_argument('--label')
    p.add_argument('--items'); p.add_argument('--count', type=int); p.add_argument('--status', choices=['done', 'failed', 'skip'])
    p.add_argument('--by'); p.set_defaults(fn=cmd_run)
    p = sub.add_parser('sink'); p.add_argument('action', choices=['add', 'status', 'import'])
    p.add_argument('--stream', default='default'); p.add_argument('--target'); p.add_argument('--provenance')
    p.add_argument('--data'); p.add_argument('--from', dest='from_file'); p.set_defaults(fn=cmd_sink)
    p = sub.add_parser('stance'); p.add_argument('action', choices=['set', 'clear', 'show'])
    p.add_argument('name', nargs='?', choices=['freeze', 'confirm'])
    p.add_argument('--memory', choices=['confirm', 'silent']); p.add_argument('--note'); p.set_defaults(fn=cmd_stance)
    p = sub.add_parser('discuss'); p.add_argument('action', choices=['open', 'close', 'list'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--thread', action='append'); p.add_argument('--choice')
    p.add_argument('--to-decision', dest='to_decision'); p.set_defaults(fn=cmd_discuss)
    p = sub.add_parser('deliverables'); p.add_argument('dirs', nargs='*'); p.set_defaults(fn=cmd_deliverables)
    p = sub.add_parser('status'); p.add_argument('--line', action='store_true'); p.set_defaults(fn=cmd_status)
    p = sub.add_parser('escalate'); p.add_argument('action', choices=['raise', 'list', 'resolve', 'retract'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--question'); p.add_argument('--domain')
    p.add_argument('--because', choices=['pivotal', 'irreversible', 'cost']); p.add_argument('--options')
    p.add_argument('--recommend'); p.add_argument('--choice'); p.add_argument('--to-decision', dest='to_decision')
    p.set_defaults(fn=cmd_escalate)
    p = sub.add_parser('ask'); p.add_argument('action', choices=['add', 'list', 'close', 'bump'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--text'); p.add_argument('--evidence')
    p.add_argument('--all', action='store_true'); p.set_defaults(fn=cmd_ask)
    p = sub.add_parser('match'); p.add_argument('query'); p.set_defaults(fn=cmd_match)
    p = sub.add_parser('accept'); p.add_argument('action', choices=['add', 'show', 'check'])
    p.add_argument('type'); p.add_argument('--criterion'); p.set_defaults(fn=cmd_accept)
    p = sub.add_parser('route'); p.add_argument('action', choices=['set', 'model', 'lead', 'check'])
    p.add_argument('klass', nargs='?'); p.add_argument('--keywords'); p.add_argument('--model'); p.set_defaults(fn=cmd_route)
    p = sub.add_parser('critique'); p.add_argument('action', choices=['assume', 'research', 'alt', 'check'])
    p.add_argument('--claim'); p.add_argument('--bearing', choices=['load', 'minor']); p.add_argument('--status', choices=['untested', 'tested', 'user-confirmed'])
    p.add_argument('--angle'); p.add_argument('--finding'); p.add_argument('--source'); p.add_argument('--gap')
    p.add_argument('--option'); p.add_argument('--because'); p.set_defaults(fn=cmd_critique)
    p = sub.add_parser('claim'); p.add_argument('resource'); p.add_argument('--by'); p.add_argument('--release', action='store_true'); p.set_defaults(fn=cmd_claim)
    p = sub.add_parser('whiteboard'); p.add_argument('action', choices=['post', 'read']); p.add_argument('message', nargs='?', default=''); p.add_argument('--by'); p.set_defaults(fn=cmd_whiteboard)
    p = sub.add_parser('search'); p.add_argument('term'); p.set_defaults(fn=cmd_search)
    p = sub.add_parser('read'); p.add_argument('--all', action='store_true'); p.add_argument('--journal-limit', type=int); p.set_defaults(fn=cmd_read)
    p = sub.add_parser('prefs'); p.add_argument('--append'); p.set_defaults(fn=cmd_prefs)
    p = sub.add_parser('state'); p.add_argument('--note'); p.set_defaults(fn=cmd_state)
    p = sub.add_parser('outcome'); p.add_argument('action', nargs='?', default='show', choices=['set', 'show', 'clear'])
    p.add_argument('text', nargs='?'); p.set_defaults(fn=cmd_outcome)
    p = sub.add_parser('checkpoint'); p.add_argument('action', choices=['add', 'status', 'choice', 'list'])
    p.add_argument('arg1', nargs='?'); p.add_argument('arg2', nargs='?'); p.add_argument('--text')
    p.add_argument('--to-decision', dest='to_decision'); p.set_defaults(fn=cmd_checkpoint)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
