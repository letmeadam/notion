import copy

from . import paragraph
from .. import block_factory


# {
#     "archived": False,
#     "bookmark": {"caption": [], "url": "https://www.wargamer.com/dnd/level-up"},
#     "created_by": {"id": "UUID", "object": "user"},
#     "created_time": "2023-10-06T19:07:00.000Z",
#     "has_children": False,
#     "id": "00e71de9-14ee-42a5-b230-8c58ed2bafc4",
#     "last_edited_by": {"id": "UUID", "object": "user"},
#     "last_edited_time": "2023-10-06T19:07:00.000Z",
#     "object": "block",
#     "parent": {"block_id": "UUID", "type": "block_id"},
#     "type": "bookmark",
# }


@block_factory.BlockFactory.register("bookmark")
class NotionBookmark(paragraph.NotionParagraph):
    BLOCK_TYPE = "bookmark"
    _TEXT_KEY = "caption"

    def _reset_patch_data(self):
        super(NotionBookmark, self)._reset_patch_data()
        bookmark_template = self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]

        # URL
        url = self.block.get(self.BLOCK_TYPE, {}).get("url", "")
        bookmark_template["url"] = url
        self.patch_data[self.BLOCK_TYPE]["url"] = url

        # Captions
        captions = self.block.get(self.BLOCK_TYPE, {}).get(self._TEXT_KEY, [])
        bookmark_template[self._TEXT_KEY] = copy.deepcopy(captions)
        self.patch_data[self.BLOCK_TYPE][self._TEXT_KEY] = copy.deepcopy(captions)

    def get_url(self, raw=False):
        if raw:
            return self.block[self.BLOCK_TYPE]["url"]
        return self.patch_data[self.BLOCK_TYPE]["url"]

    def set_url(self, new_url):
        self.patch_data[self.BLOCK_TYPE]["url"] = new_url

    def get_captions(self, raw=False):
        return self.get_texts(raw=raw)

    def set_captions(self, new_captions):
        self.set_texts(new_captions)

    def __str__(self):
        caption = super(NotionBookmark, self).__str__()
        return self._colorize_str(f'@Bookmark("{caption}", {self.get_url()})')
