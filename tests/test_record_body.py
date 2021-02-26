from logchange.record_body import RecordBody

class TestRecordBody:
    def test_parse(self):
        assert RecordBody.parse("test").render() == "test"
        assert RecordBody.parse("Added: test").render() == "### Added\ntest"
        assert RecordBody.parse("other\nAdded: test\nAdded: test2").render() == "other\n\n### Added\ntest\ntest2"
        assert RecordBody.parse("### Added\n\ntest\n\n### Added\n\ntest2").render() == "### Added\ntest\ntest2"
        assert RecordBody.parse("### Added\n\ntest\n## Other\n\ntest2").render() == "### Added\ntest\n\n## Other\n\ntest2"
