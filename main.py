#!/usr/bin/env python3
"""The World in One Day - Friday 20 November 2026.

Renders a one-page news front page as a PNG, using only the Python
standard library: a hand-drawn 5x7 bitmap font, flat-colour panels and
a zlib PNG encoder. Fully deterministic - same bytes on every run.

Writes the image to /output/entry.png (or $MAKEFUN_OUTPUT_DIR).
"""

import os
import struct
import sys
import zlib

# The grader runs this as `python3 -P -s /bot/main.py`, and -P stops Python
# from adding the script's own directory to sys.path, so do it explicitly
# before importing the sibling stories module.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from stories import LEAD_HEADLINE, LEAD_SUMMARY, NUMBERS, REGIONS, TIMELINE

W = 1024
H = 1024
MARGIN = 24
RIGHT = W - MARGIN  # 1000

PAPER = (247, 243, 233)
PANEL = (238, 231, 213)
INK = (20, 24, 29)
GREY = (58, 64, 72)
RED = (179, 35, 42)
RULE = (120, 112, 96)
TIMELINE_BG = (233, 227, 206)

# ---------------------------------------------------------------- font
# 5x7 bitmap glyphs, one string per row, '#' = ink.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("###..", "#..#.", "#...#", "#...#", "#...#", "#..#.", "###.."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".###.", "#...#", "#....", "#.###", "#...#", "#...#", ".####"),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "#...#", "##..#", "#.#.#", "#..##", "#...#", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "#.#.#", ".#.#."),
    "X": ("#...#", ".#.#.", "..#..", "..#..", "..#..", ".#.#.", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "0": (".###.", "#..##", "#.#.#", "##..#", "#...#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".##..", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".#...", "#...."),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    ":": (".....", ".##..", ".##..", ".....", ".##..", ".##..", "....."),
    ";": (".....", ".##..", ".##..", ".....", ".##..", ".#...", "#...."),
    "'": (".#...", ".#...", "#....", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "..##.", "..#..", ".....", "..#.."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("##..#", "##.#.", "....#", "...#.", "..#..", ".#.##", "#..##"),
    "+": (".....", "..#..", "..#..", ".###.", "..#..", "..#..", "....."),
    "&": (".##..", "#..#.", "#.#..", ".#...", "#.#.#", "#..#.", ".#.#."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
}

ADV = {1: 6, 2: 11, 3: 17, 4: 23, 6: 34}


def normalize(text):
    text = text.upper()
    text = text.replace("\u2019", "'").replace("\u2018", "'")
    text = text.replace("\u201c", '"').replace("\u201d", '"')
    text = text.replace("\u2014", "-").replace("\u2013", "-")
    text = text.replace("\u2026", "...")
    return "".join(ch if ch in FONT else " " for ch in text)


def text_w(text, scale):
    text = normalize(text)
    if not text:
        return 0
    return len(text) * ADV[scale] - (ADV[scale] - 5 * scale)


def wrap(text, scale, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    words = normalize(text).split()
    lines = []
    cur = ""
    for word in words:
        while text_w(word, scale) > max_w:  # over-long word: hard split
            take = max_w // ADV[scale]
            if cur:
                lines.append(cur)
                cur = ""
            lines.append(word[:take])
            word = word[take:]
        trial = word if not cur else cur + " " + word
        if text_w(trial, scale) <= max_w:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


# ---------------------------------------------------------------- canvas
class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.px = bytearray(bg * (w * h))

    def fill_rect(self, x, y, w, h, colour):
        x0 = max(0, x)
        y0 = max(0, y)
        x1 = min(self.w, x + w)
        y1 = min(self.h, y + h)
        if x1 <= x0 or y1 <= y0:
            return
        row = bytes(colour) * (x1 - x0)
        for yy in range(y0, y1):
            i = (yy * self.w + x0) * 3
            self.px[i:i + len(row)] = row

    def draw_text(self, x, y, text, scale, colour, bold=False):
        offsets = (0, max(1, scale // 3)) if bold else (0,)
        for ch in normalize(text):
            glyph = FONT[ch]
            for dy, row in enumerate(glyph):
                for dx, cell in enumerate(row):
                    if cell == "#":
                        for off in offsets:
                            self.fill_rect(x + dx * scale + off,
                                           y + dy * scale,
                                           scale, scale, colour)
            x += ADV[scale]
        return x

    def draw_centered(self, cx, y, text, scale, colour, bold=False):
        x = cx - text_w(text, scale) // 2
        return self.draw_text(x, y, text, scale, colour, bold)

    def to_png(self):
        raw = bytearray()
        stride = self.w * 3
        for yy in range(self.h):
            raw.append(0)
            raw += self.px[yy * stride:(yy + 1) * stride]

        def chunk(kind, data):
            out = struct.pack(">I", len(data)) + kind + data
            out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
            return out

        ihdr = struct.pack(">IIBBBBB", self.w, self.h, 8, 2, 0, 0, 0)
        return (b"\x89PNG\r\n\x1a\n"
                + chunk(b"IHDR", ihdr)
                + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
                + chunk(b"IEND", b""))


# ---------------------------------------------------------------- layout
def draw_masthead(cv):
    cv.draw_centered(W // 2, 8, "ONE DAY - THE WHOLE WORLD - ONE PAGE",
                     2, RED, bold=True)
    cv.draw_centered(W // 2, 26, "THE WORLD IN ONE DAY", 6, INK, bold=True)
    cv.draw_centered(W // 2, 72, "FRIDAY 20 NOVEMBER 2026", 4, RED, bold=True)
    cv.fill_rect(MARGIN, 104, RIGHT - MARGIN, 3, INK)
    cv.fill_rect(MARGIN, 109, RIGHT - MARGIN, 1, RULE)


def draw_lead(cv, top):
    x1 = 700
    cv.fill_rect(MARGIN, top, x1 - MARGIN, 122, PANEL)
    cv.fill_rect(MARGIN, top, 6, 122, RED)
    tx = MARGIN + 18
    cv.draw_text(tx, top + 8, "THE LEAD", 2, RED, bold=True)
    lines = wrap(LEAD_HEADLINE, 3, x1 - tx - 10)
    y = top + 27
    for line in lines:
        cv.draw_text(tx, y, line, 3, INK, bold=True)
        y += 23
    y += 2
    for line in wrap(LEAD_SUMMARY, 2, x1 - tx - 10):
        cv.draw_text(tx, y, line, 2, GREY)
        y += 15


def draw_numbers(cv, top):
    x0 = 712
    cv.fill_rect(x0, top, RIGHT - x0, 122, INK)
    cv.draw_centered((x0 + RIGHT) // 2, top + 7, "THE DAY IN NUMBERS",
                     2, PAPER, bold=True)
    cell_w = (RIGHT - x0) // 2
    for i, (figure, caption) in enumerate(NUMBERS):
        cx = x0 + (i % 2) * cell_w + 10
        cy = top + 25 + (i // 2) * 32
        cv.draw_text(cx, cy, figure, 3, (240, 200, 120), bold=True)
        cv.draw_text(cx, cy + 23, caption, 1, PAPER)


HEAD_H = 18
HEAD_ADV = HEAD_H + 3
HEAD_STEP = 16      # headline line pitch (glyph is 14 px tall)
SUMM_STEP = 10      # summary line pitch (glyph is 7 px tall)
HEAD_SUMM_GAP = 1   # extra space between headline and summary
STORY_GAP = 2


def story_block(headline, summary, width):
    head = wrap(headline, 2, width)
    summ = wrap(summary, 1, width)
    height = (len(head) * HEAD_STEP + HEAD_SUMM_GAP
              + len(summ) * SUMM_STEP + STORY_GAP)
    return head, summ, height


def draw_columns(cv, top, bottom):
    col_x = [MARGIN, 353, 682]
    col_w = 318
    text_off = 8
    text_w_max = col_w - text_off - 2
    col = 0
    y = top
    skipped = []

    def header(name, colour, cont=False):
        nonlocal y
        label = name + (" CONT." if cont else "")
        cv.fill_rect(col_x[col], y, col_w, HEAD_H, colour)
        cv.draw_text(col_x[col] + 8, y + 2, label, 2, PAPER, bold=True)
        y += HEAD_ADV

    for name, colour, stories in REGIONS:
        # Header + first story must fit together, else start a new column.
        first = story_block(stories[0][0], stories[0][1], text_w_max)
        need = HEAD_ADV + first[2]
        if y + need > bottom and col < 2:
            col += 1
            y = top
        if y + need > bottom:
            skipped.extend(stories)
            continue
        header(name, colour)
        for headline, summary in stories:
            head, summ, height = story_block(headline, summary, text_w_max)
            if y + height > bottom:
                if col >= 2:
                    skipped.append((headline, summary))
                    continue
                col += 1
                y = top
                header(name, colour, cont=True)
                if y + height > bottom:
                    skipped.append((headline, summary))
                    continue
            x = col_x[col]
            cv.fill_rect(x, y, 3, height - STORY_GAP, colour)
            ty = y
            for line in head:
                cv.draw_text(x + text_off, ty, line, 2, INK, bold=True)
                ty += HEAD_STEP
            ty += HEAD_SUMM_GAP
            for line in summ:
                cv.draw_text(x + text_off, ty, line, 1, GREY)
                ty += SUMM_STEP
            y += height
        y += 2
    return skipped


def draw_timeline(cv, top):
    cv.fill_rect(MARGIN, top, RIGHT - MARGIN, 60, TIMELINE_BG)
    cv.draw_text(MARGIN + 10, top + 4, "THE DAY IN UTC", 2, INK, bold=True)
    cell_w = (RIGHT - MARGIN) // 6
    for i, (time, label) in enumerate(TIMELINE):
        cx = MARGIN + (i % 6) * cell_w + 10
        cy = top + 23 + (i // 6) * 17
        cv.draw_text(cx, cy, time, 2, RED, bold=True)
        lines = wrap(label, 1, cell_w - 62)
        ly = cy
        for line in lines[:2]:
            cv.draw_text(cx + 60, ly, line, 1, INK)
            ly += 8


def draw_footer(cv):
    cv.fill_rect(MARGIN, 992, RIGHT - MARGIN, 1, RULE)
    cv.draw_centered(
        W // 2, 999,
        "SOURCES: REUTERS - AP - BBC - AL JAZEERA - IANS - OPEN CHRONICLE"
        " - WIRE REPORTS - ALL EVENTS OF FRIDAY 20 NOVEMBER 2026",
        1, GREY)


def render():
    cv = Canvas(W, H, PAPER)
    draw_masthead(cv)
    draw_lead(cv, 114)
    draw_numbers(cv, 114)
    skipped = draw_columns(cv, 236, 926)
    draw_timeline(cv, 928)
    draw_footer(cv)
    if skipped:
        print("SKIPPED %d stories: %s" % (len(skipped),
              ", ".join(s[0] for s in skipped)), file=sys.stderr)
    return cv.to_png()


def main():
    data = render()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)), file=sys.stderr)


if __name__ == "__main__":
    main()
