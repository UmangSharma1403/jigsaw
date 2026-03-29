# ── MASTER BEAD INVENTORY (19 Unique Colors Total) ─────────
# This is carefully merged to stay under your 25 max color limit.
MASTER_COLORS = {
    "black":          (0, 0, 0),
    "dark_gray":      (55, 55, 55),
    "mid_gray":       (140, 140, 140),
    "white":          (255, 255, 255),

    "skin_deep":      (62, 38, 28),
    "skin_dark":      (105, 68, 45),
    "skin_mid":       (150, 100, 68),
    "skin_light":     (190, 140, 105),
    "skin_highlight": (220, 175, 148),
    "skin_bright":    (240, 210, 190),

    "red_brown":      (130, 75, 50),
    "cream":          (210, 195, 170),

    "navy_blue":      (28, 45, 78),
    "mid_blue":       (55, 80, 120),
    "sky_blue":       (120, 170, 220),

    "dark_green":     (60, 110, 60),
    "light_green":    (140, 170, 100),

    "red":            (200, 50, 60),
    "yellow":         (230, 180, 60),
}


# ── PORTRAIT PALETTE (14 Colors) ──────────────────────────
# Excludes pure greens, pure reds, and yellows to prevent skin bleed
PORTRAIT_PALETTE = [
    MASTER_COLORS["black"], MASTER_COLORS["dark_gray"], MASTER_COLORS["mid_gray"], MASTER_COLORS["white"],
    MASTER_COLORS["skin_deep"], MASTER_COLORS["skin_dark"], MASTER_COLORS["skin_mid"], MASTER_COLORS["skin_light"],
    MASTER_COLORS["skin_highlight"], MASTER_COLORS["skin_bright"],
    MASTER_COLORS["red_brown"], MASTER_COLORS["cream"],
    MASTER_COLORS["navy_blue"], MASTER_COLORS["mid_blue"]
]

# ── GENERAL PALETTE (16 Colors) ───────────────────────────
# Has greens/reds/yellows, but uses fewer specialized skin tones
GENERAL_PALETTE = [
    MASTER_COLORS["black"], MASTER_COLORS["dark_gray"], MASTER_COLORS["mid_gray"], MASTER_COLORS["white"],
    MASTER_COLORS["skin_deep"], MASTER_COLORS["skin_mid"], MASTER_COLORS["skin_light"], MASTER_COLORS["skin_bright"],
    MASTER_COLORS["red_brown"],
    MASTER_COLORS["navy_blue"], MASTER_COLORS["sky_blue"],
    MASTER_COLORS["dark_green"], MASTER_COLORS["light_green"],
    MASTER_COLORS["red"], MASTER_COLORS["yellow"]
]

# Keep BEAD_PALETTE around so we don't break other imports
BEAD_PALETTE = GENERAL_PALETTE