import numpy as np

from ascii_art.utils import ColourSpace

CLEAR: np.ndarray = np.array([0, 0, 0, 0], dtype=np.uint8)
RESET: str = "\033[0m"

def _rgb_to_col256(r: int, g: int, b: int) -> int:
    cr, cg, cb = r // 51, g // 51, b // 51
    return 16 + 36 * cr + 6 * cg + cb

def _gen_col_code(r: int, g: int, b: int, *, mode: ColourSpace, bg: bool = False):
    """Convert a single pixel to a colour code"""
    colour_section = f"2;{r};{g};{b}" if mode == ColourSpace.TRUE else f"5;{_rgb_to_col256(r, g, b)}"
    return f"\033[{48 if bg else 38};{colour_section}m"

def _pix(top: np.ndarray, bot: np.ndarray, *, mode: ColourSpace) -> str:
    """Convert a single pair of (top, bot) in small mode"""

    # We start by assuming that top = foreground, bot = background.
    fg_r, fg_g, fg_b, fg_a = top
    bg_r, bg_g, bg_b, bg_a = bot

    # Currently, small mode does not accept alpha.
    # So we normalise alpha values to either completely opaque or completely transparent
    # We round them to either full (1) or none (0)
    fg_opaque = fg_a > 127
    bg_opaque = bg_a > 127

    # Now run through each possible case:

    # Both fully transparent
    if not fg_opaque and not bg_opaque:
        return f'{RESET} '

    # Top transparent, bottom opaque
    if not fg_opaque and bg_opaque:
        fg_colstr = _gen_col_code(bg_r, bg_g, bg_b, mode=mode)
        return f'{RESET}{fg_colstr}▄{RESET}'

    # Top opaque, bottom transparent
    if fg_opaque and not bg_opaque:
        fg_colstr = _gen_col_code(fg_r, fg_g, fg_b, mode=mode)
        return f'{RESET}{fg_colstr}▀{RESET}'

    # Both fully opaque
    fg_colstr = _gen_col_code(fg_r, fg_g, fg_b, mode=mode)
    bg_colstr = _gen_col_code(bg_r, bg_g, bg_b, mode=mode, bg=True)
    return f'{fg_colstr}{bg_colstr}▀{RESET}'

def _convert(img: np.ndarray, *, mode: ColourSpace) -> str:
    height, width, _ = img.shape
    lines = []

    for y in range(height):
        row_tokens = []
        for x in range(width):
            r, g, b, a = img[y, x]

            if a == 0:
                row_tokens.append("  ")
                continue

            if mode == ColourSpace.TRUE:
                col_code = f"\033[38;2;{r};{g};{b}m"
            else:
                col_code = f"\033[38;5;{_rgb_to_col256(r, g, b)}m"

            alpha_code = "\033[2m" if a < 255 else ""

            row_tokens.append(f"{col_code}{alpha_code}██")

        lines.append("".join(row_tokens) + "\033[0m")

    return "\n".join(lines)

def _convert_small(img: np.ndarray, *, mode: ColourSpace) -> str:
    height, width, _ = img.shape
    lines = []

    for y in range(0, height, 2):
        row_tokens = []

        for x in range(width):
            top_pix, bot_pix = img[y, x], (img[y + 1, x] if y + 1 < height else CLEAR)  # if we don't check for bounds, well then hello, IndexError!
            string = _pix(top=top_pix, bot=bot_pix, mode=mode)
            row_tokens.append(string)

        lines.append("".join(row_tokens))
    return "\n".join(lines)

def convert_img_to_ascii_art(img, *, small: bool, mode: ColourSpace) -> str:
    return (
        _convert_small(img, mode=mode)
        if small else _convert(img, mode=mode)
    )
