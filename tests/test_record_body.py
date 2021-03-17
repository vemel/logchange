import pytest
from newversion.version import Version

from logchange.record_body import RecordBody
from logchange.record_section import RecordSection


class TestRecordBody:
    def test_parse(self):
        assert RecordBody.parse("test").render() == "test"
        assert RecordBody.parse("Added: test").render() == "### Added\ntest"
        assert (
            RecordBody.parse("other\nAdded: test\nAdded: test2").render()
            == "other\n\n### Added\ntest\ntest2"
        )
        assert (
            RecordBody.parse("### Added\n\ntest\n\n### Added\n\ntest2").render()
            == "### Added\ntest\ntest2"
        )
        assert (
            RecordBody.parse("### Added\n\ntest\n## Other\n\ntest2").render()
            == "### Added\ntest\n\n## Other\n\ntest2"
        )
        body = RecordBody.parse(
            "### Added\n\ntest\n\n```\n### Removed\nnot a section\n```\n## Other\n\ntest2"
        )
        assert [i.title for i in body.sections] == ["added"]

    def test_init(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("added", "- added2\n"),
            )
        )
        assert body.render() == "### Added\n- added\n- added2\n\n### Removed\n- removed"

    def test_bump_version(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", "- fixed"),
            )
        )
        assert body.bump_version(Version("1.2.3")) == Version("2.0.0")

        body = RecordBody(
            (
                RecordSection("removed", ""),
                RecordSection("added", "- added"),
                RecordSection("fixed", "- fixed"),
            )
        )
        assert body.bump_version(Version("1.2.3")) == Version("1.3.0")

        body = RecordBody(
            (
                RecordSection("removed", ""),
                RecordSection("added", ""),
                RecordSection("fixed", "- fixed"),
            )
        )
        assert body.bump_version(Version("1.2.3")) == Version("1.2.4")
        assert RecordBody().bump_version(Version("1.2.3")) == Version("1.2.4")

    def test_bump_rc_version(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", "- fixed"),
            )
        )
        assert body.bump_rc_version(Version("1.2.3")) == Version("2.0.0rc1")
        assert body.bump_rc_version(Version("1.2.3rc1")) == Version("2.0.0rc1")
        assert body.bump_rc_version(Version("1.0.0rc1")) == Version("1.0.0rc2")

    def test_get_section(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", ""),
            )
        )
        assert body.get_section("removed").body == "- removed"
        assert body.get_section("added").body == "- added"
        assert body.get_section("fixed").body == ""
        with pytest.raises(ValueError):
            body.get_section("unknown")

    def test_set_section(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", ""),
            )
        )
        body.set_section("removed", "- new removed")
        assert body.get_section("removed").body == "- new removed"
        body.set_section("added", "")
        assert body.get_section("added").body == ""
        with pytest.raises(ValueError):
            body.set_section("unknown", "")

    def test_append_lines(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", ""),
            )
        )
        body.append_lines("removed", "\n- new removed")
        assert body.get_section("removed").body == "- removed\n- new removed"
        body.append_lines("added", "\n")
        assert body.get_section("added").body == "- added"

    def test_append_to_all(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", "- added"),
                RecordSection("fixed", ""),
            )
        )
        body.append_to_all(" postfix")
        assert body.get_section("removed").body == "- removed postfix"
        assert body.get_section("added").body == "- added postfix"
        assert body.get_section("fixed").body == ""
        assert body.get_section("security").body == ""

    def test_get_merged(self):
        body = RecordBody(
            (
                RecordSection("removed", "- removed"),
                RecordSection("added", ""),
                RecordSection("fixed", "- fixed"),
            )
        )
        body2 = RecordBody(
            (
                RecordSection("removed", "- removed2"),
                RecordSection("added", "- added"),
                RecordSection("fixed", ""),
            )
        )
        merged = body.get_merged(body2)
        assert merged.get_section("removed").body == "- removed\n- removed2"
        assert merged.get_section("added").body == "- added"
        assert merged.get_section("fixed").body == "- fixed"
        assert merged.get_section("security").body == ""

    def test_parse_prefix_section(self):
        assert RecordBody._parse_prefix_section("Added: new added") == "added"
        assert RecordBody._parse_prefix_section("added:new added") == "added"
        assert RecordBody._parse_prefix_section("removed new added") == ""
        assert RecordBody._parse_prefix_section("removed new: added") == ""
        assert RecordBody._parse_prefix_section("") == ""

    def test_is_empty(self):
        assert RecordBody().is_empty() is True
        assert RecordBody([RecordSection("fixed", "")]).is_empty() is True
        assert RecordBody(prefix="prefix").is_empty() is False
        assert RecordBody(postfix="prefix").is_empty() is False
        assert RecordBody([RecordSection("fixed", "- fixed")]).is_empty() is False

    def test_sanitize(self):
        body = RecordBody([RecordSection("added", "- added")], prefix="prefix", postfix="postfix")
        body.sanitize()
        assert body.render() == "### Added\n- added"

    def test_clone(self):
        body = RecordBody(prefix="prefix", postfix="postfix")
        assert body.clone().render() == "prefix\n\npostfix"

    def test_clear(self):
        body = RecordBody([RecordSection("added", "- added")], prefix="prefix", postfix="postfix")
        body.clear()
        assert body.render() == ""
