import copy

from . import paragraph
from .. import block_factory


# {'archived': False,
#  'callout': {'color': 'gray_background',
#              'icon': {'emoji': '⭐', 'type': 'emoji'},
#              'rich_text': []},
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-17T00:35:00.000Z',
#  'has_children': False,
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-17T00:35:00.000Z',
#  'object': 'block',
#  'parent': {'page_id': 'UUID',
#             'type': 'page_id'},
#  'type': 'callout'}


@block_factory.BlockFactory.register("callout")
class NotionCallout(paragraph.NotionParagraph):
    BLOCK_TYPE = "callout"

    _DEFAULT_EMOJI = {
        "emoji": "⭐",
        "type": "emoji",
    }

    def _reset_patch_data(self):
        super(NotionCallout, self)._reset_patch_data()
        callout_template = self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]

        # Color
        color = self.block.get(self.BLOCK_TYPE, {}).get("color", "gray_background")
        callout_template["color"] = color
        self.patch_data[self.BLOCK_TYPE]["color"] = color

        # Icon
        icon = self.block.get(self.BLOCK_TYPE, {}).get("icon", copy.copy(self._DEFAULT_EMOJI))
        callout_template["icon"] = icon
        self.patch_data[self.BLOCK_TYPE]["icon"] = copy.deepcopy(icon)

    def get_icon(self, raw=False):
        if raw:
            return self.block[self.BLOCK_TYPE]["icon"]
        return self.patch_data[self.BLOCK_TYPE]["icon"]

    def set_icon(self, icon):
        self.patch_data[self.BLOCK_TYPE]["icon"] = icon

    def __str__(self):
        output_text = "[["

        for text in self.get_texts():
            output_text += str(text)

        output_text += "]]"

        return self._colorize_str(output_text)
