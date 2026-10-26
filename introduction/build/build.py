import json, math, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

D = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, D)
from narration import SECTIONS

VOICE = os.environ.get("OFE_VOICE", os.path.join(D, "voices", "en_GB-alba-medium.onnx"))
OUT = os.path.join(D, "out"); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1920, 1080, 30
BASE_LS, NOISE, NOISE_W = 1.1, 0.72, 0.85
LEAD, GAP, TAIL, XF = 0.75, 0.5, 1.1, 0.6
IMAGES = {
    "title": "slides/title.png", "cli1": "slides/cli1.png", "cli2": "slides/cli2.png",
    "start": "slides/start.png", "modes": "slides/modes.png", "close": "slides/close.png",
    "fit": "shots/10-fit-compact.png", "figures": "shots/22-fig-clean.png", "report": "shots/31-report-full.png", "report_top": "shots/30-report.png",
}
only = set(sys.argv[1:])

# --- narration -------------------------------------------------------------
def synth():
    from piper import PiperVoice, SynthesisConfig
    v = PiperVoice.load(VOICE)
    sr = v.config.sample_rate
    clips = []
    for si, sec in enumerate(SECTIONS):
        for ji, (cap, say, ls, *_ ) in enumerate(sec["sentences"]):
            cfg = SynthesisConfig(length_scale=ls or BASE_LS, noise_scale=NOISE, noise_w_scale=NOISE_W)
            x = np.concatenate([c.audio_float_array for c in v.synthesize(say or cap, cfg)])
            env = np.convolve(np.abs(x), np.ones(220) / 220, "same")
            on = np.where(env > 10 ** (-42 / 20))[0]
            pad = int(0.03 * sr)
            x = x[max(on[0] - pad, 0): on[-1] + pad]
            clips.append(x)
    return sr, clips

def timeline(clips, sr):
    t, k, secs = 0.0, 0, []
    for sec in SECTIONS:
        s0 = t; t += LEAD; sents = []
        for j, _ in enumerate(sec["sentences"]):
            d = len(clips[k]) / sr
            sents.append((t, t + d)); t += d + GAP; k += 1
        t += TAIL - GAP
        secs.append({"start": s0, "end": t, "sents": sents})
    return secs, t

# --- captions --------------------------------------------------------------
def two_lines(s):
    if len(s) <= 42: return s
    best = None
    for m in re.finditer(" ", s):
        a, b = s[:m.start()], s[m.end():]
        if len(a) <= 42 and len(b) <= 42:
            score = abs(len(a) - len(b))
            if best is None or score < best[0]: best = (score, a + "\n" + b)
    if best: return best[1]
    sp = [m.start() for m in re.finditer(" ", s)]
    i = min(sp, key=lambda i: max(i, len(s) - i - 1))
    return s[:i] + "\n" + s[i + 1:]

def chunks(s):
    if len(s) <= 84 and two_lines(s).count("\n") <= 1 and all(len(l) <= 42 for l in two_lines(s).split("\n")):
        return [s]
    parts = re.split(r"(?<=[,:;])\s+", s)
    out, cur = [], ""
    for p in parts:
        cand = (cur + " " + p).strip()
        if cur and len(cand) > 62: out.append(cur); cur = p
        else: cur = cand
    out.append(cur)
    res = []
    for c in out:
        if len(c) > 84:
            words, cur = c.split(), ""
            for w_ in words:
                if len(cur) + len(w_) + 1 > 62 and cur: res.append(cur); cur = w_
                else: cur = (cur + " " + w_).strip()
            res.append(cur)
        else: res.append(c)
    return res

def srt_time(t):
    ms = int(round(t * 1000)); return "%02d:%02d:%02d,%03d" % (ms // 3600000, ms // 60000 % 60, ms // 1000 % 60, ms % 1000)

def captions(secs):
    cues = []
    for sec, tl in zip(SECTIONS, secs):
        for (cap, *_), (a, b) in zip(sec["sentences"], tl["sents"]):
            cs = chunks(cap); n = sum(len(c) for c in cs); t = a
            for i, c in enumerate(cs):
                d = (b - a) * len(c) / n
                cues.append([t, t + d, two_lines(c)]); t += d
            cues[-1][1] = b + 0.35
    out = []
    for i, (a, b, txt) in enumerate(cues, 1):
        out.append(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n{txt}\n")
    return "\n".join(out), cues

# --- pictures --------------------------------------------------------------
def ease(u): u = min(max(u, 0.0), 1.0); return u * u * (3 - 2 * u)
def clamp01(u): return min(max(u, 0.0), 1.0)

def cam_rect(img, cam):
    x, y, w = cam; h = w * 9 / 16
    iw, ih = img.size
    w = min(w, iw); h = w * 9 / 16
    if h > ih: h = ih; w = h * 16 / 9
    x = min(max(x, 0), iw - w); y = min(max(y, 0), ih - h)
    return (x, y, w, h)

FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)

def render_section(si, tl, imgs, t):
    sec = SECTIONS[si]; S = sec["sentences"]; sents = tl["sents"]
    k = 0
    for j, (a, b) in enumerate(sents):
        if t >= a - 0.3: k = j
    img1 = imgs[S[k][3]]
    def rect_at(j):
        return cam_rect(imgs[S[j][3]], S[j][4])
    a = sents[k][0] - 0.3
    u = ease((t - a) / 1.2) if k > 0 else 1.0
    r0 = rect_at(k - 1) if k > 0 else rect_at(0); r1 = rect_at(k)
    since = max(t - (a if k > 0 else tl["start"]), 0)
    def lerp(p, q): return tuple(pp + (qq - pp) * u for pp, qq in zip(p, q))
    iw, ih = img1.size
    def drift(r, s):
        x, y, w, h = r; f = 1 - min(0.0045 * s, 0.04)
        ax = x / (iw - w) if iw - w > 1 else 0.5
        ay = y / (ih - h) if ih - h > 1 else 0.5
        return (x + w * (1 - f) * ax, y + h * (1 - f) * ay, w * f, h * f)
    img0, img1 = imgs[S[k - 1][3]] if k > 0 else imgs[S[0][3]], imgs[S[k][3]]
    if img0 is img1:
        r = drift(lerp(r0, r1), since)
        frame = img1.resize((W, H), Image.BILINEAR, box=(r[0], r[1], r[0] + r[2], r[1] + r[3]))
    else:
        r = drift(r1, since)
        f1 = img1.resize((W, H), Image.BILINEAR, box=(r[0], r[1], r[0] + r[2], r[1] + r[3]))
        rp = drift(r0, since + 5)
        f0 = img0.resize((W, H), Image.BILINEAR, box=(rp[0], rp[1], rp[0] + rp[2], rp[1] + rp[3]))
        frame = Image.blend(f0, f1, ease((t - a) / 0.6))
    # highlight: spotlight + outline
    hl = S[k][5]
    if hl:
        boxes = hl if isinstance(hl, list) else [hl]
        nxt = S[k + 1][5] if k + 1 < len(S) else None
        alpha = clamp01((t - (sents[k][0] - 0.1)) / 0.45)
        if nxt != hl:
            end = sents[k + 1][0] - 0.3 if k + 1 < len(S) else tl["end"] - 0.2
            alpha *= clamp01((end - t) / 0.35)
        if alpha > 0:
            sx, sy = W / r[2], H / r[3]
            arr = np.asarray(frame).astype(np.float32)
            mask = np.zeros((H, W), np.float32)
            outs = []
            for (x0, y0, x1, y1) in boxes:
                X0, Y0 = int((x0 - r[0]) * sx), int((y0 - r[1]) * sy)
                X1, Y1 = int((x1 - r[0]) * sx), int((y1 - r[1]) * sy)
                mask[max(Y0, 0):max(Y1, 0), max(X0, 0):max(X1, 0)] = 1
                outs.append((X0, Y0, X1, Y1))
            arr *= (1 - 0.5 * alpha * (1 - mask))[..., None]
            frame = Image.fromarray(arr.clip(0, 255).astype(np.uint8))
            ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
            for b in outs:
                dr.rounded_rectangle(b, radius=12, outline=(242, 166, 79, int(255 * alpha)), width=5)
            frame = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
    if sec["label"]:
        la = min(clamp01((t - tl["start"] - 0.3) / 0.5), clamp01((tl["start"] + 4.5 - t) / 0.6))
        ov = Image.new("RGBA", (W, H), (0, 0, 0, 0)); dr = ImageDraw.Draw(ov)
        tw = dr.textlength(sec["label"], font=FONT)
        dr.rounded_rectangle((40, H - 98, 40 + tw + 48, H - 40), radius=29, fill=(12, 18, 22, int(215 * la)), outline=(44, 196, 181, int(255 * la)), width=3)
        dr.text((64, H - 86), sec["label"], font=FONT, fill=(228, 237, 245, int(255 * la)))
        frame = Image.alpha_composite(frame.convert("RGBA"), ov).convert("RGB")
    return frame

def main():
    sr, clips = synth()
    secs, total = timeline(clips, sr)
    audio = np.zeros(int(total * sr) + sr, np.float32); k = 0
    for tl in secs:
        for (a, b) in tl["sents"]:
            x = clips[k]; i = int(a * sr); audio[i:i + len(x)] += x; k += 1
    with wave.open(os.path.join(OUT, "narration-raw.wav"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((audio.clip(-1, 1) * 32767).astype(np.int16).tobytes())
    srt, cues = captions(secs)
    open(os.path.join(OUT, "captions.srt"), "w").write(srt)
    json.dump({"total": total, "sections": secs}, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    print("total %.1fs, %d cues, longest cue %.1fs" % (total, len(cues), max(b - a for a, b, _ in cues)))
    if "audio" in only: return
    imgs = {k_: Image.open(os.path.join(D, v)).convert("RGB") for k_, v in IMAGES.items()}
    nfr = int(math.ceil(total * FPS))
    raw = os.path.join(OUT, "video.mkv")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                           "-c:v", "libx264", "-preset", "medium", "-crf", "12", "-pix_fmt", "yuv444p", raw], stdin=subprocess.PIPE)
    frames_only = [float(x) for x in os.environ.get("FRAMES", "").split(",") if x]
    for n in range(nfr):
        t = n / FPS
        if frames_only and not any(abs(t - f) < 0.5 / FPS for f in frames_only): continue
        si = max(i for i, s in enumerate(secs) if s["start"] <= t + 1e-9)
        fr = render_section(si, secs[si], imgs, t)
        if si + 1 < len(secs) and t > secs[si]["end"] - XF / 2:
            u = (t - (secs[si]["end"] - XF / 2)) / XF
            fr = Image.blend(fr, render_section(si + 1, secs[si + 1], imgs, secs[si + 1]["start"]), ease(u))
        if si > 0 and t < secs[si]["start"] + XF / 2:
            u = (t - (secs[si]["start"] - XF / 2)) / XF
            fr = Image.blend(render_section(si - 1, secs[si - 1], imgs, secs[si - 1]["end"]), fr, ease(u))
        fade = min(clamp01(t / 0.8), clamp01((total - t) / 1.2))
        if fade < 1: fr = Image.blend(Image.new("RGB", (W, H)), fr, ease(fade))
        if frames_only: fr.save(os.path.join(OUT, "f%07.2f.png" % t)); continue
        ff.stdin.write(fr.tobytes())
        if n % 300 == 0: print("frame", n, "/", nfr, flush=True)
    ff.stdin.close(); ff.wait()

if __name__ == "__main__":
    main()
