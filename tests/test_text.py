from resumebuilder.text import wrap_text


class TestWrapText:
    def test_empty_string(self):
        assert wrap_text("", 10, 200) == []

    def test_single_short_word(self):
        lines = wrap_text("hello", 10, 200)
        assert lines == ["hello"]

    def test_multiple_lines(self):
        lines = wrap_text("hello world foo bar", 10, 45)
        assert len(lines) >= 2

    def test_long_single_word(self):
        lines = wrap_text("supercalifragilisticexpialidocious", 10, 10)
        assert lines == ["supercalifragilisticexpialidocious"]

    def test_idempotent(self):
        text = "already wrapped text"
        lines = wrap_text(text, 10, 500)
        assert len(lines) == 1

    def test_respects_max_width(self):
        text = "this is a test of word wrapping behavior"
        lines = wrap_text(text, 10, 100)
        for line in lines:
            from reportlab.pdfbase.pdfmetrics import stringWidth

            assert stringWidth(line, "Times-Roman", 10) <= 100
