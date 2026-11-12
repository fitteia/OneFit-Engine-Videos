"""Replaces the old OneFit logo in the GUI header of the captured screenshots
with the current one, without capturing them again (2026-11-12: the logo
changed to the fit line through a ring after the videos were made).

    python3 kit/new-header-logo.py LOGO.svg SHOT.png...

The old logo is found by normalised cross-correlation with a template cut
from introduction/build/shots/10-fit-compact.png (so dimmed copies behind a
dialog are found too), covered with the header's colour, and the new logo
(rendered with rsvg-convert to the same height) is put at the same centre,
dimmed by the same factor as its surroundings. A shot without the old logo
is left as it is. Run it once: the template is the old logo, which is gone
afterwards.
"""
import subprocess, sys, tempfile
import numpy as np
from PIL import Image

TEMPLATE_SHOT = "introduction/build/shots/10-fit-compact.png"
BOX = (41, 76, 87, 128)      # the old logo there, in picture pixels
BG = 26.0                    # the header's grey behind it
SEARCH = (0, 0, 900, 700)    # the headers are all in this corner
THRESHOLD = 0.85


def gray(a):
    return a[..., :3].astype(np.float64) @ [0.299, 0.587, 0.114]


def ncc(img, tpl):
    """Normalised cross-correlation of tpl over img (valid positions)."""
    th, tw = tpl.shape
    t = tpl - tpl.mean()
    tn = np.sqrt((t ** 2).sum())
    H, W = img.shape
    fs = (H + th, W + tw)
    num = np.fft.irfft2(np.fft.rfft2(img, fs) * np.conj(np.fft.rfft2(np.pad(t, ((0, H), (0, W))), fs)), fs)[:H - th + 1, :W - tw + 1]
    c1 = np.pad(img, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    c2 = np.pad(img ** 2, ((1, 0), (1, 0))).cumsum(0).cumsum(1)
    win = lambda c: c[th:, tw:] - c[:-th, tw:] - c[th:, :-tw] + c[:-th, :-tw]
    s1, s2 = win(c1), win(c2)
    var = s2 - s1 ** 2 / (th * tw)
    return num / (np.sqrt(np.maximum(var, 1e-9)) * tn)


def main():
    logo, shots = sys.argv[1], sys.argv[2:]
    ref = np.asarray(Image.open(TEMPLATE_SHOT).convert("RGB")).astype(np.float64)
    x0, y0, x1, y1 = BOX
    tpl = gray(ref[y0:y1, x0:x1])
    bgmask = np.abs(ref[y0:y1, x0:x1] - BG).sum(2) < 6
    h = y1 - y0
    TEXT = gray(ref[y0:y0 + h // 2, x1 + 12:x1 + 110]).max()
    with tempfile.NamedTemporaryFile(suffix=".png") as f:
        subprocess.run(["rsvg-convert", "-h", str(h), "-o", f.name, logo], check=True)
        new = Image.open(f.name).convert("RGBA")
        new.load()
    for path in shots:
        im = Image.open(path).convert("RGB")
        a = np.asarray(im).astype(np.float64)
        sx0, sy0, sx1, sy1 = SEARCH
        c = ncc(gray(a[sy0:sy1, sx0:sx1]), tpl)
        found = 0
        while True:
            y, x = np.unravel_index(np.argmax(c), c.shape)
            if c[y, x] < THRESHOLD:
                break
            score = c[y, x]
            X, Y = x + sx0, y + sy0
            # this header's own background (the windows differ), and how much
            # a dialog dims it: the "OneFit" text beside the logo against its
            # undimmed brightness
            bg = np.median(a[Y:Y + h, X:X + (x1 - x0)][bgmask], axis=0)
            text = gray(a[Y:Y + h // 2, X + (x1 - x0) + 12:X + (x1 - x0) + 110]).max()
            k = min(text / TEXT, 1.0)
            # wide enough for the old logo and the new one, centred on the old
            tw = max(x1 - x0, new.width) + 4
            tile = Image.new("RGBA", (tw, h + 4), (0, 0, 0, 0))
            tile.alpha_composite(new, ((tw - new.width) // 2, 2))
            ta = np.asarray(tile).astype(np.float64)
            al = ta[..., 3:] / 255
            t = (bg * (1 - al) + ta[..., :3] * k * al).clip(0, 255).astype(np.uint8)
            im.paste(Image.fromarray(t), (X + (x1 - x0) // 2 - tw // 2, Y - 2))
            a = np.asarray(im).astype(np.float64)
            c[max(y - h, 0):y + h, max(x - h, 0):x + h] = -1
            found += 1
            print(f"{path}: old logo at ({X}, {Y}), match {score:.2f}, dimmed x{k:.2f}")
        if found:
            im.save(path)
        else:
            print(f"{path}: no old logo")


if __name__ == "__main__":
    main()
