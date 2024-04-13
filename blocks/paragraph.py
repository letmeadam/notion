from __future__ import annotations

import copy
from typing import List, Union

from .. import block as notion_block
from .. import block_factory
from .. import rich_text as notion_text


@block_factory.BlockFactory.register("paragraph")
class NotionParagraph(notion_block.NotionBlock):
    BLOCK_TYPE: str = "paragraph"
    _TEXT_KEY: str = "rich_text"

    def _reset_patch_data(self):
        super(NotionParagraph, self)._reset_patch_data()
        paragraph_template = self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]

        # Color
        color = self.block.get(self.BLOCK_TYPE, {}).get("color", "default")
        paragraph_template["color"] = color
        self.patch_data[self.BLOCK_TYPE]["color"] = color

        # Rich_text
        texts = self.block.get(self.BLOCK_TYPE, {}).get(self._TEXT_KEY, [])
        paragraph_template[self._TEXT_KEY] = copy.deepcopy(texts)
        self.patch_data[self.BLOCK_TYPE][self._TEXT_KEY] = copy.deepcopy(texts)

    def get_texts(self, raw: bool = False) -> List[notion_text.NotionRichText]:
        """"""
        rich_texts = self.block.get(self.BLOCK_TYPE, {}).get(self._TEXT_KEY, [])
        if raw:
            return rich_texts

        rich_texts = copy.deepcopy(self.patch_data[self.BLOCK_TYPE][self._TEXT_KEY])
        for index, text in enumerate(rich_texts):
            text_class = notion_text.NotionRichText

            if text["type"] == "mention":
                if text["mention"]["type"] == "page":
                    text_class = notion_text.NotionPageMention
                elif text["mention"]["type"] == "date":
                    text_class = notion_text.NotionDateMention
                else:
                    text_class = notion_text.NotionMention

            rich_texts[index] = text_class.from_dict(text)

        return rich_texts

    def set_texts(self, texts: List[Union[notion_text.NotionRichText, str]] = None):
        new_texts = []

        for text in texts or []:
            if isinstance(text, str):
                text = notion_text.NotionRichText(text)
            if isinstance(text, notion_text.NotionRichText):
                new_texts.append(text.to_dict())

        self.patch_data[self.BLOCK_TYPE][self._TEXT_KEY] = new_texts

    def set_text(self, text: str | notion_text.NotionRichText = None):
        if text and not isinstance(text, list):
            text = [text]

        self.set_texts(texts=text)

    def is_empty(self) -> bool:
        texts = self.get_texts(raw=False)

        for text in texts:
            if text.plain_text:
                return False

        return True

    def lstrip(self):
        texts = self.get_texts()
        for index in range(len(texts)):
            if texts[index].plain_text.lstrip():
                break
        else:
            index = len(texts)
        self.set_texts(texts[index:])

    def rstrip(self):
        texts = self.get_texts()
        for index in reversed(range(0, len(texts))):
            stripped_text = texts[index].plain_text.rstrip()
            if stripped_text:
                index += 1
                break
        else:
            return

        self.set_texts(texts[:index])

    def strip(self):
        self.lstrip()
        if not self.is_empty():
            self.rstrip()

    def __str__(self) -> str:
        output_text = ""

        for text in self.get_texts():
            output_text += str(text)

        return self._colorize_str(output_text)
