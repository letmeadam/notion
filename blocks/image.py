from .. import block as notion_block
from .. import block_factory


# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-16T23:55:00.000Z',
#  'divider': {},
#  'has_children': False,
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-16T23:55:00.000Z',
#  'object': 'block',
#  'parent': {'page_id': 'UUID',
#             'type': 'page_id'},
#  'type': 'divider'}


@block_factory.BlockFactory.register("image")
class NotionImage(notion_block.NotionBlock):
    BLOCK_TYPE = "image"

    def __str__(self):
        return "<image>"
