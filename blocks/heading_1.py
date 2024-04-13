from . import paragraph
from .. import block_factory

# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-05T23:00:00.000Z',
#  'has_children': True,
#  'heading_1': {'color': 'default',
#                'is_toggleable': True,
#                'rich_text': [{'annotations': {'bold': False,
#                                               'code': False,
#                                               'color': 'default',
#                                               'italic': False,
#                                               'strikethrough': False,
#                                               'underline': False},
#                               'href': None,
#                               'plain_text': '🏴\u200d☠️ Dead to Water: Session '
#                                             '8 ',
#                               'text': {'content': '🏴\u200d☠️ Dead to Water: '
#                                                   'Session 8 ',
#                                        'link': None},
#                               'type': 'text'},
#                              {'annotations': {'bold': False,
#                                               'code': False,
#                                               'color': 'default',
#                                               'italic': False,
#                                               'strikethrough': False,
#                                               'underline': False},
#                               'href': None,
#                               'mention': {'date': {'end': None,
#                                                    'start': '2023-10-03',
#                                                    'time_zone': None},
#                                           'type': 'date'},
#                               'plain_text': '2023-10-03',
#                               'type': 'mention'}]},
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-06T20:31:00.000Z',
#  'object': 'block',
#  'parent': {'page_id': 'UUID',
#             'type': 'page_id'},
#  'type': 'heading_1'}


@block_factory.BlockFactory.register("heading_1")
class NotionHeading1(paragraph.NotionParagraph):
    BLOCK_TYPE = "heading_1"

    def _reset_patch_data(self):
        super(NotionHeading1, self)._reset_patch_data()
        # Is_toggleable
        is_toggleable = self.block.get(self.BLOCK_TYPE, {}).get("is_toggleable", False)
        self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]["is_toggleable"] = is_toggleable
        self.patch_data[self.BLOCK_TYPE]["is_toggleable"] = is_toggleable

    def get_toggleable(self, raw=False):
        if raw:
            return self.block[self.BLOCK_TYPE]["is_toggleable"]
        return self.patch_data[self.BLOCK_TYPE]["is_toggleable"]

    def set_toggleable(self, toggleable):
        self.patch_data[self.BLOCK_TYPE]["is_toggleable"] = toggleable

    def __str__(self):
        output_text = paragraph.NotionParagraph.__str__(self)

        if self.get_toggleable():
            output_text = " ⮟ #" + output_text

        return self._colorize_str(output_text)
