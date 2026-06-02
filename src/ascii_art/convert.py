import numpy as np

from ascii_art.utils import ColourSpace

def _rgb_to_col256(r: int, g: int, b: int) -> int:
    cr, cg, cb = r // 51, g // 51, b // 51
    return 16 + 36 * cr + 6 * cg + cb

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
    ...

def convert_img_to_ascii_art(img, *, small: bool, mode: ColourSpace) -> str:
    return (
        _convert_small(img, mode=mode)
        if small else _convert(img, mode=mode)
    )
