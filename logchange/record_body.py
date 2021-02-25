from typing import Iterable, Type, TypeVar

from newversion import Version

from logchange.constants import MAJOR_SECTION_TITLES, MINOR_SECTION_TITLES, SECTION_TITLES
from logchange.record_section import RecordSection
from logchange.utils import dedent

_R = TypeVar("_R", bound="RecordBody")


class RecordBody:
    PARTS_DELIM = "\n\n"

    def __init__(
        self,
        sections: Iterable[RecordSection] = (),
        prefix: str = "",
        postfix: str = "",
    ) -> None:
        self.sections = {i: RecordSection(i, "") for i in SECTION_TITLES}
        self.prefix = prefix
        self.postfix = postfix
        for section in sections:
            self.append_lines(section.title, section.body)

    def bump_version(self, old_version: Version) -> Version:
        for major_title in MAJOR_SECTION_TITLES:
            section = self.get_section(major_title)
            if section and not section.is_empty():
                return old_version.bump_major()

        for major_title in MINOR_SECTION_TITLES:
            section = self.get_section(major_title)
            if section and not section.is_empty():
                return old_version.bump_minor()

        return old_version.bump_micro()

    def get_section(self, title: str) -> RecordSection:
        return self.sections[title]

    def render(self) -> str:
        parts = []

        if self.prefix:
            parts.append(self.prefix)

        for section_title in SECTION_TITLES:
            section = self.get_section(section_title)
            if section.is_empty():
                continue
            parts.append(section.render())

        if self.postfix:
            parts.append(self.postfix)

        parts = [i for i in parts if i]
        return self.PARTS_DELIM.join(parts)

    def set_section(self, title: str, body: str) -> None:
        section = RecordSection(title, body)
        self.sections[section.title] = section

    def append_lines(self, title: str, body: str) -> None:
        self.sections[title].append_lines(body)

    def append_to_all(self, appendix: str) -> None:
        for section in self.sections.values():
            if not section.is_empty():
                section.append(appendix)

    def merge(self: _R, other: _R) -> _R:
        result = self.__class__()
        for section_title in SECTION_TITLES:
            old_section = self.get_section(section_title)
            new_section = other.get_section(section_title)
            result.append_lines(section_title, old_section.body)
            result.append_lines(section_title, new_section.body)

        return result

    @classmethod
    def parse(cls: Type[_R], text: str) -> _R:
        text = dedent(text)
        title = ""
        section_lines = []
        prefix_lines = []
        postfix_lines = []
        codeblock = False
        result = cls()
        for line in text.splitlines():
            if line.startswith("```"):
                codeblock = not codeblock
            if not codeblock:
                if line.startswith("#") and " " in line:
                    if section_lines:
                        result.append_lines(title, dedent("\n".join(section_lines)))
                        section_lines.clear()
                    new_title = line.split()[1].lower()
                    if new_title in SECTION_TITLES:
                        title = new_title
                        continue
                    else:
                        title = ""

            if title:
                section_lines.append(line)
            else:
                if result.is_empty():
                    prefix_lines.append(line)
                else:
                    postfix_lines.append(line)

        if section_lines:
            result.append_lines(title, dedent("\n".join(section_lines)))
        result.prefix = dedent("\n".join(prefix_lines))
        result.postfix = dedent("\n".join(postfix_lines))
        return result

    def is_empty(self) -> bool:
        for section in self.sections.values():
            if not section.is_empty():
                return False

        return True

    def sanitize(self) -> None:
        self.prefix = ""
        self.postfix = ""
