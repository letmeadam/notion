import copy

from . import paragraph
from .. import block_factory


# {'archived': False,
#  'created_by': {'id': 'UUID', 'object': 'user'},
#  'created_time': '2023-10-23T04:33:00.000Z',
#  'has_children': True,
#  'id': 'UUID',
#  'last_edited_by': {'id': 'UUID',
#                     'object': 'user'},
#  'last_edited_time': '2023-10-23T04:33:00.000Z',
#  'object': 'block',
#  'parent': {'page_id': 'UUID',
#             'type': 'page_id'},
#  'synced_block': {'synced_from': None},
#  'type': 'synced_block'}


@block_factory.BlockFactory.register("synced_block")
class NotionSyncedBlock(paragraph.NotionParagraph):
    BLOCK_TYPE = "synced_block"

    def _reset_patch_data(self):
        super(NotionSyncedBlock, self)._reset_patch_data()
        synced_block_template = self.PATCH_DATA_TEMPLATE[self.BLOCK_TYPE]

        # Synced From
        synced_from = self.block.get(self.BLOCK_TYPE, {}).get("synced_from", None)
        synced_block_template["synced_from"] = copy.deepcopy(synced_from)
        self.patch_data[self.BLOCK_TYPE]["synced_from"] = synced_from

    def get_synced_from(self, raw=False):
        if raw:
            return self.block[self.BLOCK_TYPE]["synced_from"]
        return self.patch_data[self.BLOCK_TYPE]["synced_from"]

    def is_original(self):
        return self.get_synced_from() is None

    def __str__(self):
        return "@@SyncedBlock({})".format("Original" if self.is_original() else self.get_synced_from()["block_id"])
