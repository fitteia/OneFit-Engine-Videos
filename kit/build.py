import json, math, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Run from a video's build folder (make.sh does): its narration.py holds the
# script and the pictures, and out/ there holds this build.
KIT = os.path.dirname(os.path.abspath(__file__))
D = os.getcwd()
sys.path.insert(0, D)
from narration import SECTIONS, IMAGES

VOICE = os.environ.get("OFE_VOICE", os.path.join(KIT, "voices", "en_GB-alba-medium.onnx"))
OUT = os.path.join(D, "out"); os.makedirs(OUT, exist_ok=True)
W, H, FPS = 1920, 1080, 30
BASE_LS, NOISE, NOISE_W = 1.1, 0.72, 0.85
LEAD, GAP, TAIL, XF = 0.75, 0.5, 1.1, 0.6
only = set(sys.argv[1:])

# --- narration -------------------------------------------------------------
def voiced(cap, say, ls):
    return [say or cap, ls or BASE_LS]

# Each sentence's audio; with REUSE_AUDIO, a sentence whose spoken text and
# pace are unchanged keeps its audio from the previous build (out/), so a
# change re-voices only the sentences that changed.
def synth():
    keep, sr = {}, None
    if os.environ.get("REUSE_AUDIO"):
        tl = json.load(open(os.path.join(OUT, "timeline.json")))
        with wave.open(os.path.join(OUT, "narration-raw.wav")) as w:
            sr = w.getframerate()
            raw = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32767
        spans = [ab for s_ in tl["sections"] for ab in s_["sents"]]
        for key, (a, b) in zip(tl.get("voiced", []), spans):
            keep[json.dumps(key)] = raw[int(a * sr):int(a * sr) + int(round((b - a) * sr))]
    v, clips, fresh = None, [], 0
    for si, sec in enumerate(SECTIONS):
        for ji, (cap, say, ls, *_ ) in enumerate(sec["sentences"]):
            key = json.dumps(voiced(cap, say, ls))
            if key in keep:
                clips.append(keep[key]); continue
            if v is None:
                from piper import PiperVoice, SynthesisConfig
                v = PiperVoice.load(VOICE)
                if sr is None: sr = v.config.sample_rate
            cfg = SynthesisConfig(length_scale=ls or BASE_LS, noise_scale=NOISE, noise_w_scale=NOISE_W)
            x = np.concatenate([c.audio_float_array for c in v.synthesize(say or cap, cfg)])
            env = np.convolve(np.abs(x), np.ones(220) / 220, "same")
            on = np.where(env > 10 ** (-42 / 20))[0]
            pad = int(0.03 * sr)
            x = x[max(on[0] - pad, 0): on[-1] + pad]
            clips.append(x); fresh += 1
    print("voiced %d sentence(s), reused %d" % (fresh, len(clips) - fresh))
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

# A highlight is a box (x0, y0, x1, y1) in picture pixels, a list of them, or
# a name ("slide:name") or list of names from slides/boxes.json, which
# render-slides.cjs writes for the slide elements marked data-hl.
SLIDE_BOXES = None
def hl_boxes(hl):
    global SLIDE_BOXES
    if isinstance(hl, str): hl = [hl]
    if isinstance(hl, list) and hl and isinstance(hl[0], str):
        if SLIDE_BOXES is None: SLIDE_BOXES = json.load(open(os.path.join(D, "slides", "boxes.json")))
        return [tuple(SLIDE_BOXES[n]) for n in hl]
    return hl

FONT = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", 30)

# The camera is continuous: consecutive sentences with the same picture and
# framing form one shot that keeps a slow push-in, a new framing glides there
# from wherever the camera is, and a new picture crossfades in. Nothing jumps.
DRIFT_RATE, DRIFT_MAX, GLIDE, PICTURE_XF, LEAD_IN = 0.0022, 0.03, 1.5, 0.6, 0.4

def shots(si, tl, imgs):
    S = SECTIONS[si]["sentences"]; out = []
    for j, (a, b) in enumerate(tl["sents"]):
        key = (S[j][3], tuple(S[j][4]))
        if out and out[-1]["key"] == key: continue
        start = tl["start"] if not out else a - LEAD_IN
        out.append({"key": key, "img": imgs[S[j][3]], "rect": cam_rect(imgs[S[j][3]], S[j][4]), "start": start})
    return out

def drifted(shot, t):
    x, y, w, h = shot["rect"]; iw, ih = shot["img"].size
    f = 1 - min(DRIFT_RATE * max(t - shot["start"], 0), DRIFT_MAX)
    ax = x / (iw - w) if iw - w > 1 else 0.5
    ay = y / (ih - h) if ih - h > 1 else 0.5
    return (x + w * (1 - f) * ax, y + h * (1 - f) * ay, w * f, h * f)

def camera(sh, g, t):
    if g == 0 or sh[g]["img"] is not sh[g - 1]["img"]:
        return drifted(sh[g], t)
    p, q = camera(sh, g - 1, sh[g]["start"]), drifted(sh[g], t)
    u = ease((t - sh[g]["start"]) / glide_time(p, sh[g]["rect"]))
    # zoom on a log scale (even pace whatever the ratio); the centre follows
    w = p[2] * (q[2] / p[2]) ** u; h = w * p[3] / p[2]
    cx = p[0] + p[2] / 2 + (q[0] + q[2] / 2 - p[0] - p[2] / 2) * u
    cy = p[1] + p[3] / 2 + (q[1] + q[3] / 2 - p[1] - p[3] / 2) * u
    iw, ih = sh[g]["img"].size
    return (min(max(cx - w / 2, 0), iw - w), min(max(cy - h / 2, 0), ih - h), w, h)

def glide_time(p, q):
    zoom = abs(math.log(q[2] / p[2]))
    pan = math.hypot(q[0] + q[2] / 2 - p[0] - p[2] / 2, q[1] + q[3] / 2 - p[1] - p[3] / 2) / min(p[2], q[2])
    return min(max(GLIDE, 1.0 + 0.9 * zoom + 0.6 * pan), 2.6)

def view(img, r):
    return img.resize((W, H), Image.BILINEAR, box=(r[0], r[1], r[0] + r[2], r[1] + r[3]))

def render_section(si, tl, imgs, t):
    sec = SECTIONS[si]; S = sec["sentences"]; sents = tl["sents"]
    k = 0
    for j, (a, b) in enumerate(sents):
        if t >= a - LEAD_IN: k = j
    sh = shots(si, tl, imgs)
    g = max(i for i, x in enumerate(sh) if x["start"] <= t) if t >= sh[0]["start"] else 0
    r = camera(sh, g, t)
    frame = view(sh[g]["img"], r)
    if g > 0 and sh[g]["img"] is not sh[g - 1]["img"] and t < sh[g]["start"] + PICTURE_XF:
        prev = view(sh[g - 1]["img"], camera(sh, g - 1, t))
        frame = Image.blend(prev, frame, ease((t - sh[g]["start"]) / PICTURE_XF))
    # highlight: spotlight + outline
    hl = hl_boxes(S[k][5])
    if hl:
        boxes = hl if isinstance(hl, list) else [hl]
        nxt = hl_boxes(S[k + 1][5]) if k + 1 < len(S) else None
        prv = hl_boxes(S[k - 1][5]) if k > 0 else None
        alpha = 1.0 if prv == hl else ease((t - (sents[k][0] - 0.1)) / 0.45)
        if nxt != hl:
            end = sents[k + 1][0] - LEAD_IN if k + 1 < len(S) else tl["end"] - 0.2
            alpha *= ease((end - t) / 0.35)
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
    json.dump({"total": total, "sections": secs, "voiced": [voiced(*x[:3]) for sec in SECTIONS for x in sec["sentences"]]}, open(os.path.join(OUT, "timeline.json"), "w"), indent=1)
    print("total %.1fs, %d cues, longest cue %.1fs" % (total, len(cues), max(b - a for a, b, _ in cues)))
    if "audio" in only: return
    render(secs, total)

def render(secs, total):
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
