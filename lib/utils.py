import re

ANSI_ESCAPE_CODE = re.compile(r'\x1b\[[0-9;]*m')

def raw_len(s: str) -> int:
    """Return the length of a string without ANSI escape codes."""
    raw = ANSI_ESCAPE_CODE.sub('', s)
    return len(raw)

def _test():
    test_text = "\x1b[38;5;249mHello, \x1b[31mWorld!\x1b[0m"
    print(test_text)
    assert raw_len(test_text) == 13

if __name__ == "__main__":
    _test()
