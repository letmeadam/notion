# IMPORT STANDARD LIBRARIES
from __future__ import annotations

import copy
from typing import Dict, Any

# IMPORT THIRD-PARTY LIBRARIES
import emoji

# IMPORT LOCAL LIBRARIES
from . import client
from . import rich_text as notion_text
from . import settings


# {
#     "archived": False,
#     "cover": None,
#     "created_by": {"id": "UUID", "object": "user"},
#     "created_time": "2023-10-06T19:07:00.000Z",
#     "icon": {"emoji": "🧔🏽", "type": "emoji"},
#     "id": "UUID",
#     "last_edited_by": {"id": "UUID", "object": "user"},
#     "last_edited_time": "2023-10-17T22:54:00.000Z",
#     "object": "page",
#     "parent": {"block_id": "UUID", "type": "block_id"},
#     "properties": {
#         "title": {
#             "id": "title",
#             "title": [
#                 {
#                     "annotations": {
#                         "bold": False,
#                         "code": False,
#                         "color": "default",
#                         "italic": False,
#                         "strikethrough": False,
#                         "underline": False,
#                     },
#                     "href": None,
#                     "plain_text": "Captain Redbeard",
#                     "text": {"content": "Captain Redbeard", "link": None},
#                     "type": "text",
#                 }
#             ],
#             "type": "title",
#         }
#     },
#     "public_url": "PUBLIC_URL",
#     "request_id": "UUID",
#     "url": "URL",
# }


class NotionPage(object):
    # https://developers.notion.com/reference/page
    PAGE_TYPE = "page"

    PATCH_DATA_TEMPLATE: Dict[str, Any] = {
        "object": PAGE_TYPE,
        "properties": {},
        # "cover": None,
        # "icon": None,
        "id": None,
    }
    #: dict[str, Any]: The minimum dict that can be used to patch this entity in Notion.

    def __init__(self, page: str or NotionPage):
        if isinstance(page, str):
            self.page = client.CLIENT.get_page(page)
        else:
            self.page = page

        self.id = self.page.get("id", None)
        self.PATCH_DATA_TEMPLATE["id"] = self.id

        self.PATCH_DATA_TEMPLATE["properties"] = copy.deepcopy(self.page["properties"])
        if self.page.get("icon"):
            self.PATCH_DATA_TEMPLATE["icon"] = copy.deepcopy(self.page["icon"])
        if self.page.get("cover"):
            self.PATCH_DATA_TEMPLATE["cover"] = copy.deepcopy(self.page["cover"])

        self.patch_data = copy.deepcopy(self.PATCH_DATA_TEMPLATE)

    @classmethod
    def create(cls, parent_id: NotionPage or str, title: str) -> NotionPage:
        parent_type = "page_id"
        if isinstance(parent_id, cls):
            parent_id = parent_id.id

        page_data = {
            "parent": {
                "type": parent_type,
                parent_type: parent_id,
            },
            "properties": {
                "title": {
                    "id": "title",
                    "title": [notion_text.NotionRichText(text=title).to_dict()],
                    "type": "title",
                }
            },
        }
        new_page_id = client.CLIENT.add_page(page_data)
        # logging.warning(new_page_id)
        return cls(new_page_id)

    def get_properties(self, raw: bool = False) -> Dict:
        if raw:
            return self.page["properties"]

        properties = copy.deepcopy(self.patch_data["properties"])

        for property_name, property_dict in properties.items():
            property_type = property_dict["type"]

            # Only worry about "title" and "rich_text" properties
            if property_type not in ("title", "rich_text"):
                continue

            rich_texts = []
            for text_dict in property_dict[property_type]:
                rich_texts.append(notion_text.NotionRichText.from_dict(text_dict))
            properties[property_name][property_type] = rich_texts

        return properties

    def get_title(self) -> notion_text.NotionRichText:
        return self.get_properties()["title"]["title"][0]

    def set_title(self, new_title: str):
        title_rich_text = self.get_title()
        title_rich_text.plain_text = new_title
        self.patch_data["properties"]["title"]["title"] = [title_rich_text.to_dict()]

    def has_emoji_icon(self, raw: bool = False) -> bool:
        source = self.patch_data
        if raw:
            source = self.page
        icon_dict = source.get("icon", {})
        return icon_dict.get("type") == "emoji"

    def get_icon(self, raw: bool = False) -> str:
        source = self.patch_data
        if raw:
            source = self.page
        # if raw:
        icon_dict = source["icon"]

        if icon_dict["type"] == "emoji":
            return icon_dict["emoji"]

        return icon_dict["external"]["url"]

    def set_icon(self, new_icon: str, icon_type: str = ""):
        # Emoji: {"emoji": "🧔🏽", "type": "emoji"}
        # or
        # External:
        # {
        #     "type": "external",
        #     "external": {
        #         "url": "https://images.unsplash.com/photo-1525310072745-f49212b5ac6d?ixlib=rb-1.2.1&ixid=MnwxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8&auto=format&fit=crop&w=1065&q=80"
        #     },
        # }
        if icon_type == "emoji" or emoji.emoji_count(new_icon):
            new_icon_dict = {"emoji": new_icon, "type": "emoji"}
        else:  # NOTE: what about "file" types?
            new_icon_dict = {"external": {"url": new_icon}, "type": "external"}

        self.patch_data["icon"] = new_icon_dict

    def get_cover(self, raw: bool = False) -> str:
        source = self.patch_data
        if raw:
            source = self.page

        cover_dict = source["cover"]
        return cover_dict[cover_dict["type"]]["url"]

    # def update_title(self, new_title):
    #     properties = self.get_properties()
    #     properties["title"]["title"][0]["plain_text"] = new_title
    #     properties["title"]["title"][0]["text"]["content"] = new_title
    #
    #     self.patch(
    #         {
    #             "object": "page",
    #             "id": self.id,
    #             "properties": properties,
    #         }
    #     )

    def patch(self, patch_data: Dict or None = None) -> bool:
        if not patch_data:
            patch_data = self.patch_data
            self.patch_data = copy.deepcopy(self.PATCH_DATA_TEMPLATE)

        result = client.CLIENT.patch_page(self.id, patch_data)
        self.page.update(patch_data)

        return result

    def delete(self):
        self.archive()

    def archive(self):
        if not self.is_archived():
            client.CLIENT.delete_page(self.id)

    def is_archived(self):
        return self.page["archived"]

    def get_full_title(self) -> str:
        emoji_text = ""
        if self.has_emoji_icon():
            emoji_ = self.get_icon()
            if not settings.PRINT_EMOJIS:
                emoji_ = emoji.demojize(emoji_)
            emoji_text = f"{emoji_} "

        title = self.get_title()
        return f"{emoji_text}{title}"

    def __str__(self) -> str:
        return f"[[{self.get_full_title()}]]"


#     "properties": {
#         "title": {
#             "id": "title",
#             "title": [
#                 {
#                     "annotations": {
#                         "bold": False,
#                         "code": False,
#                         "color": "default",
#                         "italic": False,
#                         "strikethrough": False,
#                         "underline": False,
#                     },
#                     "href": None,
#                     "plain_text": "Captain Redbeard",
#                     "text": {"content": "Captain Redbeard", "link": None},
#                     "type": "text",
#                 }
#             ],
#             "type": "title",
#         }
#     },

# TODO: un-give up on this :D
# class NotionPageProperty(object):
#     CHECKBOX_TYPE = "checkbox"
#     CREATED_BY_TYPE = "created_by"
#     CREATED_TIME_TYPE = "created_time"
#     DATE_TYPE = "date"
#     EMAIL_TYPE = "email"
#     FILES_TYPE = "files"
#     FORMULA_TYPE = "formula"
#     LAST_EDITED_BY_TYPE = "last_edited_by"
#     LAST_EDITED_TIME_TYPE = "last_edited_time"
#     MULTI_SELECT_TYPE = "multi_select"
#     NUMBER_TYPE = "number"
#     PEOPLE_TYPE = "people"
#     PHONE_NUMBER_TYPE = "phone_number"
#     RELATION_TYPE = "relation"
#     RICH_TEXT_TYPE = "rich_text"
#     ROLLUP_TYPE = "rollup"
#     SELECT_TYPE = "select"
#     STATUS_TYPE = "status"
#     TITLE_TYPE = "title"
#     URL_TYPE = "url"
#
#     def __init__(self, property_values, property_id=None, property_type=TITLE_TYPE):
#         self.data = {
#             property_type: property_values,
#             "type": property_type,
#             "id": property_id,
#         }
