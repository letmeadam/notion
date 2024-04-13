# IMPORT STANDARD LIBRARIES
from __future__ import annotations

import copy
import functools
import textwrap
from typing import Generator, Dict, List, Union, Any

# IMPORT THIRD-PARTY LIBRARIES
if hasattr(functools, "cached_property"):
    cached_property = functools.cached_property
else:
    # In case this needs to be used in Python 2?
    from cached_property import cached_property
import colorize

# IMPORT LOCAL LIBRARIES
from . import block_factory
from . import client as notion_client
from . import settings


@block_factory.BlockFactory.register_base_class()
class NotionBlock(object):
    # TODO: A schema would be nice...
    # PATCH_SCHEMA = {
    #     "type": "object",
    #     "properties": {
    #         "object": {"type": "string", "default": "block", },
    #         "id" {"type": "string", },
    #         "type": {
    #             "type": "string",
    #             "default": "block",
    #             "enum": [
    #                 "bookmark",
    #                 "breadcrumb",
    #                 "bulleted_list_item",
    #                 "callout",
    #                 "child_database",
    #                 "child_page",
    #                 "column",
    #                 "column_list",
    #                 "divider",
    #                 "embed",
    #                 "equation",
    #                 "file",
    #                 "heading_1",
    #                 "heading_2",
    #                 "heading_3",
    #                 "image",
    #                 "link_preview",
    #                 "link_to_page",
    #                 "numbered_list_item",
    #                 "paragraph",
    #                 "pdf",
    #                 "quote",
    #                 "synced_block",
    #                 "table",
    #                 "table_of_contents",
    #                 "table_row",
    #                 "template",
    #                 "to_do",
    #                 "toggle",
    #                 "unsupported",
    #                 "video",
    #             ]
    #         },
    #     },
    #     "required": ["object", "id", "type", ],
    # }

    OBJECT_TYPE = "block"
    BLOCK_TYPE = "block"

    PATCH_DATA_TEMPLATE: Dict[str, Any] = {
        "object": OBJECT_TYPE,
        "id": None,
        "type": BLOCK_TYPE,
    }
    #: dict[str, Any]: The minimum dict that can be used to patch this entity in Notion.

    def __init__(self, block: Union[str, Dict[str, Any], NotionBlock] = None):
        if isinstance(block, str):
            block = notion_client.CLIENT.get_block(block)
        elif isinstance(block, NotionBlock):
            block = block.block

        self.block = block if block else copy.deepcopy(self.get_patch_template())
        self.OBJECT_TYPE = self.block.get("object", self.OBJECT_TYPE)
        self.id = self.block.get("id", None)

        self.PATCH_DATA_TEMPLATE = copy.deepcopy(self.get_patch_template())
        self.PATCH_DATA_TEMPLATE["object"] = self.OBJECT_TYPE
        self.PATCH_DATA_TEMPLATE["id"] = self.id
        self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE] = {}
        self.PATCH_DATA_TEMPLATE["type"] = self.BLOCK_TYPE

        self._reset_patch_data()

    def _reset_patch_data(self):
        """Reset the internal patch data cache."""
        self.patch_data = copy.deepcopy(self.PATCH_DATA_TEMPLATE)

    @classmethod
    def get_patch_template(cls) -> Dict[str, Any]:
        return cls.PATCH_DATA_TEMPLATE

    def parent(self) -> str:
        """Get this block's parent ID."""
        parent_dict = self.block["parent"]
        parent_type = parent_dict["type"]
        parent_id = parent_dict[parent_type]
        return parent_id

    def iter_children(self) -> Generator[NotionBlock]:
        """Create a generator that yields as it steps to each child block."""
        if not self.block.get("has_children"):
            return

        notion_blocks = notion_client.CLIENT.get_block_children(self.id)
        for notion_block in notion_blocks:
            wrapper_class = block_factory.BlockFactory.get(notion_block["type"])
            yield wrapper_class(notion_block)

        self.refresh()

    @cached_property
    def children(self) -> List[NotionBlock]:
        """Cache the block's children for quicker user later."""
        if not self.block.get("has_children"):
            return []

        return list(self.iter_children())

    def add_children(self, blocks: list[Dict[str, Any] or NotionBlock], after: str = "") -> Dict[str, Any]:
        """Add the given blocks as children to this block.

        Todo:
            I need to remove `after` since it's not quite supported yet by Notion :(

        """
        for index, block in enumerate(blocks):
            if isinstance(block, NotionBlock):
                blocks[index] = block.patch_data

        patch_data = {"children": []}
        for block in blocks:
            patch_data["children"].append(
                {
                    "object": block["object"],
                    "type": block["type"],
                    block["type"]: copy.deepcopy(block[block["type"]]),
                }
            )

        if after:
            patch_data["after"] = after

        result = self.patch(patch_data, append=True)
        self.block["has_children"] = True
        self.refresh()

        return result

    def add_child(self, block: Union[Dict[str, Any], NotionBlock], after: str = "") -> Dict[str, Any]:
        """Add the given block as a child to this block.

        Todo:
            I need to remove `after` since it's not quite supported yet by Notion :(

        """
        return self.add_children([block], after=after)

    def __getitem__(self, idx: int) -> None or NotionBlock:
        """Conveniently use indices to refer to the child blocks."""
        if not self.children:
            return None

        return self.children[idx]

    def refresh(self):
        """Reset all internally cached data

        Todo:
            Perhaps this should also include `_reset_patch_data()`?

        """
        if "children" in self.__dict__:
            del self.__dict__["children"]

    def get_color(self, raw: bool = False) -> str:
        """"""
        if raw:
            return self.block[self.BLOCK_TYPE].get("color", "")
        return self.patch_data[self.BLOCK_TYPE].get("color", "")

    def set_color(self, new_color: str):
        if self.get_color(raw=True):  # Only if "color" existed already
            self.patch_data[self.BLOCK_TYPE]["color"] = new_color

    def patch(self, patch_data: Dict or None = None, append: bool = False) -> Dict:
        # If no patch_data is given, use block's patch data and reset it
        if not self.id:
            # self.block.update(patch_data)
            return {}

        if not patch_data:
            patch_data = self.patch_data
            self.patch_data = copy.deepcopy(self.PATCH_DATA_TEMPLATE)

        result = notion_client.CLIENT.patch_block(self.id, patch_data, append=append)
        self.block.update(patch_data)
        self._reset_patch_data()
        # self.block = notion_client.CLIENT.get_block(self.id)

        return result

    def delete(self):
        notion_client.CLIENT.delete_block(self.id)

    def _colorize_str(self, input_str: str) -> str:
        if settings.PRINT_COLOR:
            # print("Color: ", self.get_color())
            return colorize.colorize_string(input_str, self.get_color())
        return input_str

    def __str__(self):
        return self._colorize_str("<Unknown block>")

    def read(self, depth: int = -1, indents: int = 0):
        """
        Args:
            depth (int, optional):
                The depth of hierarchy to read through.
                0 reads ends the recursion while -1 reads the entire hierarchy.
            indents (int, optional):
                The number of indents to print the read block at. This should be increased
                automatically as this method traverses the block's children hierarchy.

        """
        if depth == 0:
            return

        print(textwrap.indent(str(self), "    " * indents))
        for child in self.children:
            child.read(depth - 1, indents + 1)
