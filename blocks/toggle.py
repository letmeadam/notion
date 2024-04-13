from . import paragraph
from .. import block_factory

# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-06T19:07:00.000Z',
#  'has_children': True,
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-06T19:37:00.000Z',
#  'object': 'block',
#  'parent': {'page_id': 'UUID',
#             'type': 'page_id'},
#  'toggle': {'color': 'default',
#             'rich_text': [{'annotations': {'bold': False,
#                                            'code': False,
#                                            'color': 'default',
#                                            'italic': False,
#                                            'strikethrough': False,
#                                            'underline': False},
#                            'href': None,
#                            'plain_text': 'Test',
#                            'text': {'content': 'Test', 'link': None},
#                            'type': 'text'}]},
#  'type': 'toggle'}


@block_factory.BlockFactory.register("toggle")
class NotionToggle(paragraph.NotionParagraph):
    BLOCK_TYPE = "toggle"

    def __str__(self):
        return self._colorize_str(" ⮟ {}".format(super(NotionToggle, self).__str__()))
