"""
Converter between Unix and WIndows line endings.
"""


class EOLFixer:
    """
    Converter between Unix and WIndows line endings.
    """

    WINDOWS_LINE_ENDING = "\r\n"
    UNIX_LINE_ENDING = "\n"

    @classmethod
    def is_windows(cls, text: str) -> bool:
        """
        Check whether text has `\r\n` characters.

        Arguments:
            text -- Text to check.
        """
        return cls.WINDOWS_LINE_ENDING in text

    @classmethod
    def to_unix(cls, text: str) -> str:
        """
        Convert `\r\n` to `\n`.

        Arguments:
            text -- Text to convert.

        Returns:
            Converted text.
        """
        if not cls.is_windows(text):
            return text

        return text.replace(cls.WINDOWS_LINE_ENDING, cls.UNIX_LINE_ENDING)

    @classmethod
    def to_windows(cls, text: str) -> str:
        """
        Convert `\n` to `\r\n`.

        Arguments:
            text -- Text to convert.

        Returns:
            Converted text.
        """
        if cls.is_windows(text):
            return text

        return text.replace(cls.UNIX_LINE_ENDING, cls.WINDOWS_LINE_ENDING)
