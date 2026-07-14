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
          layout · feedback · run · sink · stance · escalate · ask     (--version prints the installed version)
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
        else: t = 'other'
        tagged.append((t, os.path.relpath(ap, ROOT) if ap.startswith(ROOT) else ap))
    return tagged


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
    blocking, advisory = [], []  # (summary, fix-command) — split so exit-1 means "do not build", not "mtime moved"
    if _maybe_intro():
        print()
    print('=' * 70); print(f'KEEL REHYDRATE — digest across all tiers  (keel {KEEL_VERSION})'); print('=' * 70)
    st = _stance()
    if st:
        st['rehydrates_since'] = st.get('rehydrates_since', 0) + 1
        json.dump(st, open(STANCE, 'w'))
        print(f'\n>>> STANDING STANCE: {st["name"]} (set {st["rehydrates_since"]} rehydrate(s) ago)'
              + (' — FREEZE: no builds/edits/ops' if st.get('freeze') else '')
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
    print(f'\nPROFILE: {_read(PROFILE).strip() or "(unset — run: docs.py profile <name>)"}')
    mdirs = _memory_dirs()
    print('MEMORY tiers found: ' + (', '.join((os.path.relpath(d, ROOT) if d.startswith(ROOT) else d) for d in mdirs) or '(none)'))

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
        if t in ('anchor', 'data-model'):
            print(f'   [{t}] {rel}')
    print(f'   [decisions] {ndec} · [journal] {njrn}')
    if other:
        print(f'   [other] {" · ".join(other)}   ← surfaced, read on demand')

    decs = _decisions()
    print(f'\n--- DECISIONS: {len(decs)} ADR(s) ---')
    for d in decs[-12:]:
        title = next((l for l in _read(d).splitlines() if l.strip()), os.path.basename(d))
        print('   ' + title.strip('# ').strip()[:88])

    stale = _anchor_staleness()
    if stale:
        advisory.append((f'anchor {len(stale)} edit(s) behind reality', 'docs.py hydrate'))
        print(f'\n[!] ANCHOR STALE — {len(stale)} file(s) changed after the anchor: {stale[:6]}')
        print('    → the first thing a session reads is behind reality. Run `hydrate` to refresh it.')

    contra = _contradictions()
    if contra:
        blocking.append((f'{len(contra)} live contradiction(s) — an unmarked ADR is superseded', f'docs.py supersede {contra[0][2]} --title "..."'))
        print(f'\n[!!] CONTRADICTIONS — {len(contra)} lower-tier correction(s) supersede an unmarked ADR:')
        for tier, path, n, line in contra[:8]:
            print(f'    ADR {n}: {tier}:{path} says "{line}"')
        print(f'    → do NOT act on the stale ADR. Resolve with `docs.py supersede {contra[0][2]}` first.')

    sus = _suspect_decisions()
    if sus:
        advisory.append((f'suspect decision(s) {sus} referenced as superseded but not marked', 'review + docs.py supersede if real'))
        print(f'\n[!] SUSPECT (referenced as superseded, not marked): {sus}')

    pend = [x for x in _load_jsonl(PENDING) if not x.get('drained')]
    if pend:
        advisory.append((f'{len(pend)} unflushed decision/journal item(s) from a prior session', 'docs.py hydrate'))
        print(f'\n[!] {len(pend)} UNFLUSHED item(s) from a prior session (visible debt):')
        for x in pend[-6:]:
            print(f'    {x.get("kind")}: {x.get("title", "")[:80]}' + ('  (DRAFT)' if x.get('staged') else ''))
        print('    → run `docs.py hydrate` to land/drain them.')

    if os.path.exists(VERIFY_STAMP):
        s = json.load(open(VERIFY_STAMP))
        if s.get('result') != 'pass':
            blocking.append(('last audit FAILED — deliverable is not in a passing state', 'docs.py verify run'))
            print('\n[!!] VERIFY FAILED — the last audit did not pass.')
            print('    → fix, then re-run: docs.py verify run; "done" is gated on it (`verify done`).')
        elif s.get('deliverables') != _deliverable_hash():
            advisory.append(('verify stamp stale — deliverables changed since last passing audit', 'docs.py verify run'))
            print('\n[!] VERIFY STALE — deliverables changed since the last PASSING audit (files moved/edited).')
            print('    → re-run to confirm still-green: docs.py verify run')

    hyg = _hygiene_problems()
    if hyg:
        advisory.append((f'{len(hyg)} hygiene issue(s) in deliverable dirs', 'docs.py hygiene'))
        print(f'\n[!] HYGIENE — {len(hyg)} issue(s), e.g.: {hyg[0]}')
        print('    → run `docs.py hygiene` for the full list.')

    parked = []
    for rid, s in _open_runs():
        npend = len(s['pending']) if isinstance(s['pending'], list) else s['pending']
        agem = int((time.time() - s['last_ts']) // 60)
        if agem > 7 * 24 * 60:  # >7 days idle: collapse to one compact line — never silent, never noisy
            parked.append(rid); continue
        age = f'{agem // 1440}d ago' if agem >= 1440 else (f'{agem // 60}h ago' if agem >= 60 else f'{agem}m ago')
        advisory.append((f'run {rid} mid-flight: {len(s["done"])}/{s["total"] or "?"} done, {npend} pending ({age})', f'docs.py run resume {rid}  (or `run close {rid}` to abandon)'))
        print(f'\n[!] RUN MID-FLIGHT — {rid} "{s["man"].get("label")}": {len(s["done"])}/{s["total"] or "?"} done, '
              f'{npend} pending, {len(s["failed"])} failed, last mark {age}' + ('  [STALLED]' if agem >= 10 else ''))
        print(f'    → resume where it left off: docs.py run resume {rid}   (do NOT restart from 0)')
    if parked:
        advisory.append((f'{len(parked)} run(s) parked idle >7 days: {", ".join(parked)}', 'docs.py run status <id> — then resume or close'))
        print(f'\n[!] PARKED — {len(parked)} run(s) idle >7 days: {", ".join(parked)} (resume or `run close`; never auto-deleted)')

    for stream, n, tgt in _unreconciled_sink():
        advisory.append((f'{n} captured record(s) in "{stream}" not yet merged into {tgt or "target"}', f'docs.py sink import --stream {stream}'))
        print(f'\n[!] CAPTURE INBOX — {n} record(s) in "{stream}" captured but not merged into {tgt or "target"}:')
        print(f'    → fetched data at risk of disposal. Reconcile: docs.py sink import --stream {stream}')

    open_asks = [r for r in _load_asks() if r['status'] == 'open']
    hot_asks = [r for r in open_asks if r['raised'] >= 3]
    if hot_asks:
        advisory.append((f'{len(hot_asks)} ask(s) raised 3+ times still open', 'address, or docs.py ask close <id> --evidence <path>'))
        print(f'\n[!] RECURRING ASK(S) — raised 3+ times and still open:')
        for r in sorted(hot_asks, key=lambda r: -r['raised'])[:4]:
            print(f'    #{r["id"]} raised {r["raised"]}x: {r["text"][:84]}')
    if open_asks:
        print(f'\n--- OPEN ASKS: {len(open_asks)} standing user ask(s) (docs/asks.md) ---')
        for r in sorted(open_asks, key=lambda r: -r['raised'])[:5]:
            print(f'    #{r["id"]} raised {r["raised"]}x: {r["text"][:84]}')

    js = sorted(glob.glob(os.path.join(JRN, '*.md')))
    print(f'\n--- newest journal --- ' + (os.path.basename(js[-1]) if js else '(none)'))
    if blocking or advisory:
        print('\n--- CORRECTIVE ACTIONS (' + f'{len(blocking)} blocking · {len(advisory)} advisory) ---')
        for i, (msg, fix) in enumerate(blocking, 1):
            print(f'  [B{i}] {msg}\n       → {fix}')
        for i, (msg, fix) in enumerate(advisory, 1):
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
    st = _stance()
    if st and st.get('freeze'):
        staged = [x for x in _load_jsonl(PENDING) if not x.get('drained') and x.get('staged')]
        sys.exit(f'hydrate: FROZEN — stance "{st["name"]}" blocks landing into docs/. '
                 f'{len(staged)} draft(s) staged and safe; `docs.py stance clear` first, then hydrate.')
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
        st = _stance()
        if st and st.get('freeze'):
            print(f'contract check: ✗ FROZEN — standing stance "{st["name"]}" blocks ALL builds (even lightweight lane).'
                  f'\n  note: {st.get("note") or "(none)"}   lift with: docs.py stance clear'); sys.exit(1)
        esc_open = [r for r in _load_jsonl(ESCALATIONS) if r.get('status') == 'open']
        if esc_open:
            print(f'contract check: ✗ BLOCKED-ON-USER — {len(esc_open)} open escalation(s) (#'
                  + ', #'.join(str(r["id"]) for r in esc_open[:4]) + '). Resolve before building.'); sys.exit(1)
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
        merged, refused = 0, 0
        for r in new:
            tgt = r.get('target')
            if not tgt:
                continue
            payload = r.get('payload') or (_read(r['blob']) if r.get('blob') else '')
            tp = os.path.join(ROOT, tgt)
            if tgt.endswith('.csv') and os.path.exists(tp):
                # CSV-aware: never duplicate the header; refuse column-count mismatches loudly
                header = _read(tp).splitlines()[0] if _read(tp).strip() else ''
                lines = [l for l in payload.splitlines() if l.strip() and l.strip() != header.strip()]
                bad = [l for l in lines if header and l.count(',') != header.count(',')]
                if bad:
                    refused += 1
                    print(f'  [!] REFUSED {r["hash"]}: {len(bad)} row(s) have {bad[0].count(",") + 1} column(s), '
                          f'target has {header.count(",") + 1} — fix the payload; not corrupting {tgt}.')
                    continue
                payload = '\n'.join(lines)
                if not payload:
                    rec.add(r['hash']); continue
            _ensure(os.path.dirname(tp) or ROOT)
            with open(tp, 'a', encoding='utf-8') as f:
                f.write(payload.rstrip('\n') + '\n')
            rec.add(r['hash']); merged += 1
        open(recp, 'w').write('\n'.join(sorted(rec)))
        print(f'sink import {a.stream}: {len(rows)} buffered → {merged} new merged, {len(rows) - len(new)} already present'
              + (f', {refused} REFUSED (column mismatch)' if refused else '') + '.')
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
        rows = _load_jsonl(ESCALATIONS)
        tgt = next((r for r in rows if r.get('id') == a.id and r.get('status') == 'open'), None)
        if not tgt:
            sys.exit(f'no open escalation #{a.id}')
        tgt['status'] = 'retracted' if a.action == 'retract' else 'resolved'
        tgt['choice'] = a.choice
        with open(ESCALATIONS, 'w') as f:
            for r in rows:
                f.write(json.dumps(r) + '\n')
        if a.action == 'resolve' and a.to_decision:
            n = _next_adr()
            body = f'## Context\nEscalation #{a.id}: {tgt.get("question")}\n\n## Decision\n{a.choice}\n\n## Rejected\n{tgt.get("options") or "(other options)"}\n'
            _emit_record('decision', f'{n:04d}-{_slug(a.to_decision)}.md', f'# {n:04d} — {a.to_decision}\n\n{body}\n',
                         DEC, False, a.to_decision, {'n': n})
        print(f'escalation #{a.id} {tgt["status"]}' + (f' → choice: {a.choice}' if a.choice else ''))


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
    open(ASKS_MD, 'w').write(hdr + '\n'.join(
        f'- [{r["status"]}] #{r["id"]} (raised {r["raised"]}x) {r["text"]}'
        + (f' — evidence: {r["evidence"]}' if r.get('evidence') else '') for r in rows) + '\n')


def cmd_ask(a):
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
    elif a.action == 'list':
        for r in rows:
            if r['status'] == 'open' or a.all:
                print(f'  #{r["id"]} [{r["status"]}] raised {r["raised"]}x: {r["text"][:90]}')
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


def main():
    ap = argparse.ArgumentParser(prog='docs.py', description='keel memory + enforcement CLI')
    ap.add_argument('--version', action='version', version=f'keel {KEEL_VERSION}')
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
    p = sub.add_parser('escalate'); p.add_argument('action', choices=['raise', 'list', 'resolve', 'retract'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--question'); p.add_argument('--domain')
    p.add_argument('--because', choices=['pivotal', 'irreversible', 'cost']); p.add_argument('--options')
    p.add_argument('--recommend'); p.add_argument('--choice'); p.add_argument('--to-decision', dest='to_decision')
    p.set_defaults(fn=cmd_escalate)
    p = sub.add_parser('ask'); p.add_argument('action', choices=['add', 'list', 'close', 'bump'])
    p.add_argument('id', nargs='?', type=int); p.add_argument('--text'); p.add_argument('--evidence')
    p.add_argument('--all', action='store_true'); p.set_defaults(fn=cmd_ask)
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
