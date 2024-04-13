from . import paragraph
from .. import block_factory

# {
#     "archived": False,
#     "bulleted_list_item": {
#         "color": "default",
#         "rich_text": [
#             {
#                 "annotations": {
#                     "bold": False,
#                     "code": False,
#                     "color": "default",
#                     "italic": False,
#                     "strikethrough": False,
#                     "underline": False,
#                 },
#                 "href": None,
#                 "plain_text": "a Homunculus we found on "
#                 "the abandoned Fae "
#                 "“island” of the "
#                 "exploding Fae ferns and "
#                 "the Rusted knight "
#                 "golem-king",
#                 "text": {
#                     "content": "a Homunculus we "
#                     "found on the "
#                     "abandoned Fae "
#                     "“island” of the "
#                     "exploding Fae "
#                     "ferns and the "
#                     "Rusted knight "
#                     "golem-king",
#                     "link": None,
#                 },
#                 "type": "text",
#             }
#         ],
#     },
#     "created_by": {"id": "UUID", "object": "user"},
#     "created_time": "2023-10-06T19:07:00.000Z",
#     "has_children": False,
#     "id": "UUID",
#     "last_edited_by": {"id": "UUID", "object": "user"},
#     "last_edited_time": "2023-10-06T19:07:00.000Z",
#     "object": "block",
#     "parent": {"page_id": "UUID", "type": "page_id"},
#     "type": "bulleted_list_item",
# }


@block_factory.BlockFactory.register("bulleted_list_item")
class NotionBulletedItem(paragraph.NotionParagraph):
    BLOCK_TYPE = "bulleted_list_item"

    def __str__(self):
        output_text = super(NotionBulletedItem, self).__str__()
        output_text = " • " + output_text
        return self._colorize_str(output_text)
