# Dry-run: build filtergraphs for a normal clip and a MEASURED clip.
# Graph contract (rules.md / tool-routing.md, synced 2026-09-29):
#   4 inputs [0]=src [1]=PILL [2]=LCS [3]=CS
#   hook 1-15 (0.5s fades, x=0 y=84) | LCS full 5s 25->30 auto-removed (NO freeze)
#   CS 60->69.4 K-bounce (+20% size: scale=991, x=44.5 y=534.6 re-anchored),
#   loop-hold f296 (never tpad/trim/setpts+60/gte(t,60))
import os
import encode_stage4 as E

for nn_int in (1, 13, 15):
    fc = E.build_fc(f"{nn_int:02d}", 78.0, nn_int)
    assert "[vout]" in fc and "[aout]" in fc and "{ln}" not in fc
    # center-subscribe popup: input [3], 991 wide (+20%, user 2026-09-29),
    # per-frame K-scale bounce, loop-hold on the last VISIBLE frame (f296;
    # tail f297-299 empty). K expands inline -> assert around it.
    assert "[3:v]format=rgba,scale=991:-2,loop=loop=-1:size=1:start=296,scale=w='max(2,991*" in fc
    assert "':h=-2:eval=frame[cs]" in fc
    assert "[t2][cs]overlay=x='44.5+495.5*(1-" in fc
    assert "':y='534.6+279*(1-" in fc
    assert "':enable='between(t,60,69.4)'[t3]" in fc
    # like-comment-subscribe: full 5s asset plays 25->30, auto-removed (NO freeze)
    assert "[2:v]format=rgba,setpts=PTS+25/TB[lcs]" in fc
    assert "[t1][lcs]overlay=x=268:y=56:enable='gte(t,25)'[t2]" in fc
    # freeze-hold/old-window chains are PERMANENTLY REMOVED (old bugs: clone
    # of empty tail / SUBSCRIBE frozen to clip end / gte(t,60) hold-to-end /
    # setpts+60 clock split) and Bell/YS must never come back
    for bad in ("tpad", "trim=duration", "PTS+55/TB", "PTS+60/TB",
                "between(t,55,65)", "gte(t,60)", "scale=826", "y=584", "y=179",
                "notification", "youtube-subscribe", "[4:v]", "[5:v]", "t4]"):
        assert bad not in fc, f"removed element present: {bad}"
    assert E.CS.endswith("center-subscribe.mov") and os.path.isfile(E.CS)
    ln = "measured_I" in fc
    print(f"nn={nn_int} ok len={len(fc)} measured_loudnorm={ln}")
    if nn_int == 13:
        i = fc.index("[0:a]")
        print("  audio chain:", fc[i:i + 260].split("\n")[0])
print("build_fc OK")
