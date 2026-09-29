# Generates ASS captions with word-level active highlight (v2.3 EXACT spec).
# Montserrat Bold 96px MIXED CASE -> rendered cap height 43px (size/position
# still matched to v2_hook.png; user confirmed 2026-09-26: the "38-44px" spec
# = visible cap height, em stays 96). Every visual line is its own Dialogue
# with an explicit \an8\pos — line pitch 71.5px, last line ink top at y=1464
# (bottom blur zone: below the 864px hero band 384..1248; baseline = ink
# top+43 = 1507, descenders reach ~1520 — nothing overlaid there).
# v2.3 changes (user 2026-09-26): MIXED CASE (reference subs contain
# lowercase -> no .upper()) and tracking {\fsp-0.5} (spec "0 to -0.5px /
# -1% to 0%", replacing v2.2's reference-measured -4).
# ACTIVE_RISE y-6.82 on popped lines (fscy110 inflates line ascent 10% -> the
# normal lines stay on the pitch grid, matching the reference).
# Active word: #FFE500 + 10% pop (scale 110). Inactive: #FFFFFF. Outline 4px black.
# Renderer note: the ass filter maps Fontsize to the winAscent+winDescent cell,
# so scale k = upem/(winA+winD) = 0.640 for Montserrat -> cap = 0.448 * Fontsize.
# Usage: python gen_ass.py <start_sec> <end_sec> <out.ass>
import re, html, sys, math

SRC = r"D:\youtube system\output\transcript\en\plain.txt"  # ALWAYS EN transcript (Captions Rule)
if len(sys.argv) > 4:
    SRC = sys.argv[4]          # optional: override transcript (SRT) path
WIDTH = 16       # max chars per rendered line (ref wrap: "AND WE'RE GONNA"=15)
CHUNK = 48       # max chars per caption unit (<=3 lines, ref shows 3)

# --- geometry matched to v2_hook.png reference frame -------------------------
FONT_SIZE = 96       # ass renders this at cap height 43px (0.448 * 96)
LINE_PITCH = 71.5    # ref ink tops 1321 / 1394 / 1464 -> 71.5 avg
LAST_INK_TOP = 1464.0  # bottom line ink top (ref line 3: 1464..1506)
BOX_DELTA = 25       # \an8 box top -> ink top at 96px (measured via ass filter)
ACTIVE_RISE = 6.82   # the \fscy110 pop inflates the line ascent by 10%
                     # (0.1 * 0.7100 * 96 = 6.82 -> baseline drops, cap top +7).
                     # Popped lines are shifted up by this so every line's
                     # normal caps stay on the pitch grid (ref L2: pop sticks
                     # up 4px WITHOUT moving the line).
TRACKING = -0.5      # {\fsp-0.5} — user spec v2.3: "0 to -0.5px / -1% to 0%"
                     # (normal to slightly tight). Replaces v2.2's -4 (measured
                     # from the caps-only reference: 585 vs 642). Style
                     # Spacing field negatives are ignored by libass -> must
                     # stay the per-line {\fsp} override.
CX = 540             # centered (ref cx=539)
ACT = "&H0000E5FF"   # #FFE500 BGR — active word
INA = "&H00FFFFFF"   # #FFFFFF BGR — inactive words (also the style default)

def ts_to_sec(h, m, s, ms):
    return int(h)*3600 + int(m)*60 + int(s) + int(ms)/1000.0

def sec_to_ass(sec):
    if sec < 0: sec = 0.0
    h = int(sec // 3600); m = int((sec % 3600) // 60); s = sec % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def chunk_words(words, max_chars=CHUNK):
    """Split word list into caption units of <=max_chars, balanced (min 1 word)."""
    total = sum(len(w) + 1 for w in words)
    if total <= max_chars: return [words]
    n = max(2, math.ceil(total / max_chars))
    target = total / n
    units, cur, cur_len = [], [], 0
    for w in words:
        wl = len(w) + 1
        if cur and cur_len + wl > target and len(units) < n - 1:
            units.append(cur); cur = [w]; cur_len = wl
        else:
            cur.append(w); cur_len += wl
    if cur: units.append(cur)
    return units

def wrap_lines(words, width=WIDTH):
    """Greedy wrap word list -> list of word-lists (order preserved)."""
    lines, cur, cur_len = [], [], 0
    for w in words:
        wl = len(w) + (1 if cur else 0)
        if cur and cur_len + wl > width:
            lines.append(cur); cur = [w]; cur_len = len(w)
        else:
            cur.append(w); cur_len += wl
    if cur: lines.append(cur)
    return lines

def build_line_text(line_words, active_gi, line_start):
    """One visual line; highlight the word whose global index == active_gi."""
    parts = []
    for j, w in enumerate(line_words):
        if line_start + j == active_gi:
            # yellow + scale 100->110 over 0.1s (10% pop), then reset
            parts.append("{\\c&H0000E5FF&\\t(0,10,\\fscx110\\fscy110)}" + w +
                         "{\\fscx100\\fscy100\\c&H00FFFFFF&}")
        else:
            parts.append(w)
    return " ".join(parts)

def main():
    if len(sys.argv) < 4:
        sys.exit("usage: python gen_ass.py <start_sec> <end_sec> <out.ass>")
    start = float(sys.argv[1]); end = float(sys.argv[2]); out = sys.argv[3]

    pat = re.compile(r'^\[(\d{2}):(\d{2}):(\d{2}),(\d{3})\]\s*(.*)$')
    entries = []
    for line in open(SRC, encoding="utf-8"):
        m = pat.match(line.rstrip("\n"))
        if not m: continue
        t = ts_to_sec(*m.groups()[:4])
        txt = html.unescape(m.group(5)).strip()
        txt = re.sub(r'>>\s*', '', txt)
        txt = re.sub(r'\[[^\]]*\]', '', txt)
        txt = re.sub(r'\s+', ' ', txt).strip()   # MIXED CASE per v2.3 (no .upper())
        entries.append((t, txt))

    sel = [(t, txt) for (t, txt) in entries if start <= t < end and txt]
    if not sel:
        sys.exit("no transcript entries in window")

    events = []   # (start_str, end_str, text) — boundaries formatted ONCE (no gaps)
    for (t, txt) in sel:
        abs_idx = entries.index((t, txt))
        nxt = entries[abs_idx + 1][0] if abs_idx + 1 < len(entries) else end
        e = min(nxt - 0.04, end)
        if e <= t: e = min(t + 1.0, end)
        rel_s, rel_e = t - start, e - start
        if rel_e - rel_s <= 0.05: continue

        units = chunk_words(txt.split())
        u_total = sum(sum(len(w) + 1 for w in u) for u in units)
        acc = rel_s
        for u in units:
            u_chars = sum(len(w) + 1 for w in u)
            u_dur = (rel_e - rel_s) * (u_chars / u_total)
            w_tot = sum(len(w) + 1 for w in u)
            # per-word boundaries, formatted once and shared (contiguous, zero gap)
            bnds, seen = [acc], 0
            for w in u[:-1]:
                seen += len(w) + 1
                bnds.append(acc + u_dur * seen / w_tot)
            bnds.append(acc + u_dur)
            fb = [sec_to_ass(b) for b in bnds]
            # split unit into visual lines; each line gets its own Dialogue at
            # a fixed \pos (all lines of a slot show simultaneously so only the
            # active word is yellow — same visual as one multi-line block).
            ulines = wrap_lines(u)
            lstart, gi0 = [], 0
            for ln in ulines:
                lstart.append(gi0); gi0 += len(ln)
            nl = len(ulines)
            for wi in range(len(u)):
                for li, ln in enumerate(ulines):
                    y = LAST_INK_TOP - (nl - 1 - li) * LINE_PITCH - BOX_DELTA
                    act = wi if lstart[li] <= wi < lstart[li] + len(ln) else -1
                    if act != -1:
                        y -= ACTIVE_RISE   # cancel fscy110 ascent inflation
                    body = build_line_text(ln, act, lstart[li])
                    events.append((fb[wi], fb[wi + 1],
                                   f"{{\\an8\\pos({CX},{y:g})\\fsp{TRACKING}}}" + body))
            acc += u_dur

    header = """[Script Info]
Title: YouTube Shorts Caption Style v2.3
ScriptType: v4.00+
WrapStyle: 0
ScaledBorderAndShadow: yes
YCbCr Matrix: TV.709
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: MainCaption,Montserrat,96,&H00FFFFFF,&H0000E5FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,3,2,20,20,400,1
Style: HookBanner,Montserrat,40,&H00000000,&H00FFFFFF,&H00FFFFFF,&H80000000,-1,0,0,0,100,100,0,0,3,0,0,8,20,20,240,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = [header]
    for s, e, txt in events:
        lines.append(f"Dialogue: 0,{s},{e},MainCaption,,0,0,0,,{txt}\n")
    open(out, "w", encoding="utf-8-sig").write("".join(lines))
    print(f"wrote {out}: {len(events)} word events, {len(sel)} transcript lines")

if __name__ == "__main__":
    main()
