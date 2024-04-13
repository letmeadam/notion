from __future__ import annotations

from typing import Dict, List, Union


class NotionAnnotations(object):

    """A class to manage annotation data from Notion."""

    def __init__(
        self,
        bold: bool = False,
        code: bool = False,
        color: str = "default",
        italic: bool = False,
        strikethrough: bool = False,
        underline: bool = False,
    ):
        self.bold = bold
        self.code = code
        self.color = color
        self.italic = italic
        self.strikethrough = strikethrough
        self.underline = underline

    def to_dict(self) -> Dict[str, Union[str, bool]]:
        """Convert this object into a dictionary."""
        return {
            "bold": self.bold,
            "code": self.code,
            "color": self.color,
            "italic": self.italic,
            "strikethrough": self.strikethrough,
            "underline": self.underline,
        }

    @classmethod
    def from_dict(cls, dict_: Dict[str, Union[str, bool]]) -> NotionAnnotations:
        """Create an instance of this object using the provided dictionary."""
        dict_kwargs = {}

        for key in frozenset(("bold", "code", "color", "italic", "strikethrough", "underline")):
            if dict_.get(key) is not None:
                dict_kwargs[key] = dict_[key]

        return cls(**dict_kwargs)

    def get_colorize_tokens(self) -> List[str]:
        """Gather all tokens suitable for colorizing an output.

        Note:
            This is expected to be used by colorize later.

        """
        tokens: List[str] = []

        if self.italic:
            tokens += "italic"

        if self.underline:
            tokens += "underline"

        if self.bold:
            tokens += "bold"

        if self.color != "default":
            tokens += self.color

        return tokens

    def __eq__(self, other):
        """bool: True if this object is equivalent to the other, False otherwise."""
        return self.to_dict() == other.to_dict()
