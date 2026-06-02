from toolbox_lib.utils import raw_len

def make_dialog_box(text: str) -> str:
    """Creates a dialog box from a list of lines."""
    lines = text.splitlines()

    max_line_len = max((raw_len(line) for line in lines), default=0)

    body: list[str] = []
    for line in lines:
        body.append(f"│ {line}{' ' * (max_line_len - raw_len(line))} │\n")

    dialog_box = (
        f"┌{'─' * (max_line_len + 2)}┐\n"
        + "".join(body)
        + f"└{'─' * (max_line_len + 2)}┘"
    )

    return dialog_box

def _test():
    test_cases = [
        "Hello, World!",
        "Multiline text\nThis is the second line",
        "Short line",
        "Line with colour codes: \033[31mRed\033[0m and \033[32mGreen\033[0m.",
        "Multiline message with formatting codes and Unicode characters:\n\033[1m\033[92m↑ 0:00:23\033[0m\n\033[2mThis is some faint text.\033[0m",
        ""  # Empty string test case
    ]

    for test_case in test_cases:
        print(make_dialog_box(test_case))

if __name__ == "__main__":
    _test()
