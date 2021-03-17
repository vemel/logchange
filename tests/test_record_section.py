import pytest

from logchange.record_section import RecordSection


class TestRecordBody:
    def test_render(self):
        assert RecordSection("added", "test").render() == "### Added\ntest"
        assert RecordSection("added", "\ntest").render() == "### Added\ntest"
        assert RecordSection("changed", "\n").render() == "### Changed"

        section = RecordSection("changed", "\n")
        section.body = "\n\ntest\ntest2\n"
        assert section.render() == "### Changed\ntest\ntest2"

        with pytest.raises(ValueError):
            RecordSection("none", "body")

    def test_is_valid_title(self):
        assert RecordSection.is_valid_title("added") is True
        assert RecordSection.is_valid_title("notes") is False

    def test_append(self):
        section = RecordSection("changed", "test\n")
        section.append("\n\ntest2\n")
        assert section.render() == "### Changed\ntest\n\ntest2"
        section.append("\n")
        assert section.render() == "### Changed\ntest\n\ntest2"

    def test_append_lines(self):
        section = RecordSection("changed", "test\n")
        section.append_lines("\n\ntest2\n")
        assert section.render() == "### Changed\ntest\ntest2"
        section.append_lines("test3")
        assert section.render() == "### Changed\ntest\ntest2\ntest3"
        section.append_lines("\n")
        assert section.render() == "### Changed\ntest\ntest2\ntest3"
