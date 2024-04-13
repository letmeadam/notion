import textwrap

from .. import block as notion_block
from .. import block_factory
from .. import page as notion_page


# {
#     "archived": False,
#     "child_page": {"title": "Captain Redbeard"},
#     "created_by": {"id": "UUID", "object": "user"},
#     "created_time": "2023-10-06T19:07:00.000Z",
#     "has_children": True,
#     "id": "UUID",
#     "last_edited_by": {"id": "UUID", "object": "user"},
#     "last_edited_time": "2023-10-17T22:54:00.000Z",
#     "object": "block",
#     "parent": {"block_id": "UUID", "type": "block_id"},
#     "type": "child_page",
# }


@block_factory.BlockFactory.register("child_page")
class NotionChildPage(notion_block.NotionBlock):
    BLOCK_TYPE = "child_page"

    def _reset_patch_data(self):
        super(NotionChildPage, self)._reset_patch_data()
        child_page_template = self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]

        # Title
        title = self.block.get(self.BLOCK_TYPE, {}).get("title", "Untitled")
        child_page_template["title"] = title
        self.patch_data[self.BLOCK_TYPE]["title"] = title

    def get_title(self, raw: bool = False) -> str:
        if raw:
            return self.block[self.BLOCK_TYPE]["title"]

        return self.patch_data[self.BLOCK_TYPE]["title"]

    def set_title(self, title="Untitled"):
        self.patch_data[self.BLOCK_TYPE]["title"] = title

    def __str__(self):
        page = notion_page.NotionPage(self.id)
        return self._colorize_str(f"[({page.get_full_title()})]")

    def read(self, depth=-1, indents=0):
        if depth == 0:
            return

        print(textwrap.indent(str(self), "    " * indents))

        # TODO check this "not indents" logic again...
        if not indents:
            for child in self.children:
                child.read(depth - 1, indents + 1)
