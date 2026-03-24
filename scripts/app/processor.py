import os
import numpy as np
import cv2
from PIL import Image, ImageEnhance, ImageDraw, ImageFilter
from skimage import color as skcolor
from .palette import BEAD_PALETTE

GRID_W = 70
GRID_H = 70
CELL_PIXELS = 20
GRID_LINE_COLOR = (0, 0, 0)
GRID_LINE_WIDTH = 1
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── Build LAB palette ONCE at startup ────────────────────
PALETTE_ARR    = np.array(BEAD_PALETTE, dtype=np.float32) / 255.0
PALETTE_LAB    = skcolor.rgb2lab(
    PALETTE_ARR.reshape(len(BEAD_PALETTE), 1, 3)
).reshape(len(BEAD_PALETTE), 3)
PALETTE_RGB_U8 = np.array(BEAD_PALETTE, dtype=np.uint8)


def detect_portrait(img_cv: np.ndarray) -> bool:
    """
    Returns True only if a large close-up face is detected.
    Face must cover >5% of total image area.
    """
    h, w     = img_cv.shape[:2]
    gray     = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )
    if len(faces) == 0:
        return False
    largest    = max(faces, key=lambda f: f[2] * f[3])
    face_ratio = (largest[2] * largest[3]) / (h * w)
    return face_ratio > 0.05


def portrait_crop(img: Image.Image, img_cv: np.ndarray) -> Image.Image:
    """
    Crop around detected face with padding.
    Forces square output.
    """
    h, w     = img_cv.shape[:2]
    gray     = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    detector = cv2.CascadeClassifier(
        cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    )
    faces = detector.detectMultiScale(
        gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
    )

    x1 = int(np.min(faces[:, 0]))
    y1 = int(np.min(faces[:, 1]))
    x2 = int(np.max(faces[:, 0] + faces[:, 2]))
    y2 = int(np.max(faces[:, 1] + faces[:, 3]))
    fw = x2 - x1
    fh = y2 - y1

    x1 = max(0, x1 - int(fw * 0.4))
    y1 = max(0, y1 - int(fh * 0.7))
    x2 = min(w, x2 + int(fw * 0.4))
    y2 = min(h, y2 + int(fh * 0.5))

    cw = x2 - x1
    ch = y2 - y1
    if cw > ch:
        diff = cw - ch
        y1   = max(0, y1 - diff // 2)
        y2   = min(h, y2 + diff // 2)
    else:
        diff = ch - cw
        x1   = max(0, x1 - diff // 2)
        x2   = min(w, x2 + diff // 2)

    return img.crop((x1, y1, x2, y2))


def saliency_crop(img: Image.Image, img_cv: np.ndarray) -> Image.Image:
    """
    For non-portrait images — saliency crop around main subject.
    Falls back to center square crop if saliency fails.
    """
    h, w = img_cv.shape[:2]

    saliency   = cv2.saliency.StaticSaliencyFineGrained_create()
    _, sal_map = saliency.computeSaliency(img_cv)
    sal_map    = (sal_map * 255).astype(np.uint8)
    _, thresh  = cv2.threshold(sal_map, 128, 255, cv2.THRESH_BINARY)
    coords     = cv2.findNonZero(thresh)

    if coords is not None:
        x, y, cw, ch = cv2.boundingRect(coords)

        pad = int(max(cw, ch) * 0.2)
        x   = max(0, x - pad)
        y   = max(0, y - pad)
        cw  = min(w - x, cw + 2 * pad)
        ch  = min(h - y, ch + 2 * pad)

        if cw > ch:
            diff = cw - ch
            y    = max(0, y - diff // 2)
            ch   = min(h - y, ch + diff)
        else:
            diff = ch - cw
            x    = max(0, x - diff // 2)
            cw   = min(w - x, cw + diff)

        crop = img.crop((x, y, x + cw, y + ch))
        if crop.width > w * 0.2 and crop.height > h * 0.2:
            return crop

    # Fallback — center square crop
    size = min(w, h)
    left = (w - size) // 2
    top  = (h - size) // 2
    return img.crop((left, top, left + size, top + size))


def letterbox_resize(img: Image.Image, size: tuple) -> Image.Image:
    # Force square crop (center) if not already square
    w, h = img.size
    if w != h:
        side = min(w, h)
        left = (w - side) // 2
        top  = (h - side) // 2
        img  = img.crop((left, top, left + side, top + side))

    # Now it's square — simple resize, no stretching needed
    return img.resize(size, Image.LANCZOS)


def enhance(img: Image.Image) -> Image.Image:
    img = ImageEnhance.Sharpness(img).enhance(2.0)
    img = ImageEnhance.Contrast(img).enhance(1.5)
    img = ImageEnhance.Brightness(img).enhance(1.1)
    return img


def vectorized_knn(img: Image.Image) -> np.ndarray:
    pixels     = np.array(img, dtype=np.float32) / 255.0
    pixels_lab = skcolor.rgb2lab(pixels)
    flat_lab   = pixels_lab.reshape(-1, 3)
    diff       = flat_lab[:, np.newaxis, :] - PALETTE_LAB[np.newaxis, :, :]
    distances  = np.linalg.norm(diff, axis=2)
    nearest    = np.argmin(distances, axis=1)
    return nearest.reshape(GRID_H, GRID_W)


def render_grid(grid_labels: np.ndarray) -> Image.Image:
    colored    = PALETTE_RGB_U8[grid_labels]
    scaled     = colored.repeat(CELL_PIXELS, axis=0).repeat(CELL_PIXELS, axis=1)
    output_img = Image.fromarray(scaled, mode="RGB")
    draw       = ImageDraw.Draw(output_img)
    total_w    = GRID_W * CELL_PIXELS
    total_h    = GRID_H * CELL_PIXELS
    for x in range(0, total_w + 1, CELL_PIXELS):
        draw.line([(x, 0), (x, total_h)], fill=GRID_LINE_COLOR, width=GRID_LINE_WIDTH)
    for y in range(0, total_h + 1, CELL_PIXELS):
        draw.line([(0, y), (total_w, y)], fill=GRID_LINE_COLOR, width=GRID_LINE_WIDTH)
    return output_img


def process_image(img: Image.Image):
    """
    Pipeline:
      1. Convert to RGB
      2. Detect portrait (large face >5% of image)
      3. Crop:
           Portrait → face crop with padding
           General  → saliency crop → fallback center square
      4. Letterbox resize to 50x50
      5. Enhance
      6. Vectorized KNN in LAB space
      7. Render 1000x1000 grid
    """
    img    = img.convert("RGB")
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    if detect_portrait(img_cv):
        print('   Image type: portrait')
        img = portrait_crop(img, img_cv)
    else:
        print('   Image type: general — saliency crop')
        img = saliency_crop(img, img_cv)

    img         = letterbox_resize(img, (GRID_W, GRID_H))
    img         = enhance(img)
    grid_labels = vectorized_knn(img)
    output_img  = render_grid(grid_labels)

    return output_img, grid_labels