from . import paragraph
from .. import block_factory


@block_factory.BlockFactory.register("quote")
class NotionQuote(paragraph.NotionParagraph):
    BLOCK_TYPE = "quote"

    def __str__(self):
        normal_text = super(NotionQuote, self).__str__()

        output_text = ""
        for text in normal_text.split("\n"):
            output_text += f" | {text}\n"

        return self._colorize_str(output_text)
