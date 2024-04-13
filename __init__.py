from . import block_factory
from . import client as notion_client
from . import page


def retrieve_block(block_id: str) -> Notion.block.NotionBlock:  # This is just "itching" for a cyclic import :(
    """Request and wrap the given block with a registered block class

    Arguments:
        block_id (str):
            A UUID string without the `-` characters.

    Returns:
        Notion.block.NotionBlock:
            The suitable, registered block object, or the generic if no matches found.

    """
    raw_block = notion_client.CLIENT.get_block(block_id)
    block_type = raw_block["type"]
    block_class = block_factory.BlockFactory.get(block_type)
    return block_class(raw_block)


def retrieve_page(page_id: str) -> page.NotionPage:
    """Request and wrap the given page into a NotionPage object.

    Arguments:
        page_id (str):
            A UUID string without the `-` characters.

    Returns:
        Notion.page.NotionPage:
            The page object.

    """
    return page.NotionPage(page_id)
