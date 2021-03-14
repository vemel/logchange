"""
Keep a Changelog section.
"""
from logchange.constants import SECTION_TITLES
from logchange.utils import dedent


class RecordSection:
    """
    Keep a Changelog section.

    Arguments:
        title -- Section title
        body -- Section text
    """

    def __init__(self, title: str, body: str) -> None:
        title = title.lower()
        if title not in SECTION_TITLES:
            raise ValueError(f"Invalid section title: {title}")

        self.title: str = title
        self.body: str = body

    @staticmethod
    def is_valid_title(title: str) -> bool:
        """
        Check whether `title` presents in Keep a Changelog.
        """
        return title.lower() in SECTION_TITLES

    def is_empty(self) -> bool:
        """
        Whether body is empty.
        """
        return self.body == ""

    def render(self) -> str:
        """
        Render in Keep a Changelog format.
        """
        return f"### {self.title.capitalize()}\n{dedent(self.body)}"

    def append(self, text: str) -> None:
        """
        Append `text` to section body.
        """
        self.body = dedent(f"{self.body}{text}")

    def append_lines(self, text: str) -> None:
        """
        Append `text` to section body after new line.
        """
        self.append(f"\n{text}")
