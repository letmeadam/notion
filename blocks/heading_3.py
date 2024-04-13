# import copy

from . import heading_1
from . import paragraph
from .. import block_factory

# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-06T19:04:00.000Z',
#  'has_children': False,
#  'heading_3': {'color': 'default',
#                'is_toggleable': True,
#                'rich_text': [{'annotations': {'bold': False,
#                                               'code': False,
#                                               'color': 'default',
#                                               'italic': False,
#                                               'strikethrough': False,
#                                               'underline': False},
#                               'href': None,
#                               'plain_text': '<setting>',
#                               'text': {'content': '<setting>', 'link': None},
#                               'type': 'text'}]},
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-06T19:04:00.000Z',
#  'object': 'block',
#  'parent': {'block_id': 'UUID',
#             'type': 'block_id'},
#  'type': 'heading_3'}


@block_factory.BlockFactory.register("heading_3")
class NotionHeading3(heading_1.NotionHeading1):
    BLOCK_TYPE = "heading_3"

    def __str__(self):
        output_text = paragraph.NotionParagraph.__str__(self)

        if self.get_toggleable():
            output_text = " ⮟ ###" + output_text

        return self._colorize_str(output_text)
