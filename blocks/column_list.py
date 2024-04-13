import textwrap

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


@block_factory.BlockFactory.register("column_list")
class NotionColumnList(notion_block.NotionBlock):
    BLOCK_TYPE = "column_list"

    def __str__(self):
        return "<column list>"

    def read(self, depth=-1, indents=0):
        if depth == 0:
            return

        print(textwrap.indent(str(self), "    " * indents))

        if not indents:
            for index, child in enumerate(self.children):
                print(textwrap.indent(f"Column #{index}", "    " * indents))
                child.read(depth - 1, indents)
