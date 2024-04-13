# import copy

from . import heading_1
from . import paragraph
from .. import block_factory

# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-06T19:04:00.000Z',
#  'has_children': False,
#  'heading_2': {'color': 'default',
#                'is_toggleable': True,
#                'rich_text': [{'annotations': {'bold': False,
#                                               'code': False,
#                                               'color': 'default',
#                                               'italic': False,
#                                               'strikethrough': False,
#                                               'underline': False},
#                               'href': None,
#                               'plain_text': '✨New Characters 👥',
#                               'text': {'content': '✨New Characters 👥',
#                                        'link': None},
#                               'type': 'text'}]},
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-06T19:04:00.000Z',
#  'object': 'block',
#  'parent': {'block_id': 'UUID',
#             'type': 'block_id'},
#  'type': 'heading_2'}


@block_factory.BlockFactory.register("heading_2")
class NotionHeading2(heading_1.NotionHeading1):
    BLOCK_TYPE = "heading_2"

    def __str__(self):
        output_text = paragraph.NotionParagraph.__str__(self)

        if self.get_toggleable():
            output_text = " ⮟ ##" + output_text

        return self._colorize_str(output_text)
