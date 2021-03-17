import textwrap


def strip_empty_lines(text: str) -> str:
    """
    Remove empty lines from the start and end of `text`.
    """
    lines = text.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)

    while lines and not lines[-1].strip():
        lines.pop()
    return "\n".join(lines)


def dedent(text: str) -> str:
    """
    Dendent text and remove empty lines from beginning and end.
    """
    return textwrap.dedent(strip_empty_lines(text))
