# IMPORT STANDARD LIBRARIES
from __future__ import annotations

from typing import Dict, Tuple, Union

# IMPORT THIRD-PARTY LIBRARIES
import colorize
# IMPORT LOCAL LIBRARIES
from . import annotations as notion_annotations
from . import client
from . import settings


class NotionRichText(object):
    def __init__(
        self,
        text: str = "",
        href: str or None = None,
        rich_text: object or None = None,
    ):
        self.annotations = notion_annotations.NotionAnnotations()
        self.href = href
        self.plain_text = text

        if rich_text:
            self.annotations = notion_annotations.NotionAnnotations.from_dict(rich_text.annotations.to_dict())
            # self.href = href if href is not None else rich_text.href
            # self.plain_text = text if text is not None else rich_text.plain_text

    @property
    def type(self) -> str:
        return "text"

    def to_dict(self) -> Dict:
        return {
            "annotations": self.annotations.to_dict(),
            "href": self.href,
            "plain_text": self.plain_text,
            "text": {
                "content": self.plain_text,
                "link": {"url": self.href} if self.href else None,
            },
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> NotionRichText:
        # Initial creation
        new_instance = cls(data.get("plain_text", ""), href=data.get("href"))

        # Annotations
        _annotations = data.get("annotations", dict())
        if isinstance(_annotations, dict):
            _annotations = notion_annotations.NotionAnnotations.from_dict(_annotations)
        new_instance.annotations = _annotations

        return new_instance

    def split(self, index: int) -> Tuple[NotionRichText, NotionRichText]:
        split_class_a = self.from_dict(self.to_dict())
        split_class_b = self.from_dict(self.to_dict())

        split_class_a.plain_text = split_class_a.plain_text[:index]
        split_class_b.plain_text = split_class_b.plain_text[index:]

        return split_class_a, split_class_b

    def _annotate_string(self, input_str: str):
        color_tokens = self.annotations.get_colorize_tokens() if settings.PRINT_COLOR else []
        return colorize.colorize_string(input_str, *color_tokens)

    def __str__(self) -> str:
        if self.href:
            return self._annotate_string(f"({self.plain_text})[{self.href}]")

        return self._annotate_string(self.plain_text)

    def __eq__(self, other):
        return self.to_dict() == other.to_dict()

    def can_merge_with(self, other: NotionRichText) -> bool:
        annotations_matches = self.annotations == other.annotations
        href_matches = self.href == other.href
        type_matches = self.type == other.type
        return annotations_matches and href_matches and type_matches

    def merge(self, other: NotionRichText) -> NotionRichText:
        # if not self.can_merge_with(other):
        #     return [self, other]

        self.plain_text += other.plain_text
        return self


# def split_text


class NotionMention(NotionRichText):
    @property
    def type(self) -> str:
        return "mention"

    @property
    def mention_type(self):
        return ""

    def to_dict(self) -> Dict:
        return {
            "annotations": self.annotations.to_dict(),
            "href": self.href,
            "mention": {},
            "plain_text": self.plain_text,
            "type": self.type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> NotionMention:
        # Initial creation
        new_instance = cls(text=data.get("plain_text", ""), href=data.get("href"))

        # Annotations
        _annotations = data.get("annotations")
        if _annotations:
            if isinstance(_annotations, dict):
                _annotations = notion_annotations.NotionAnnotations.from_dict(_annotations)
            new_instance.annotations = _annotations

        return new_instance

    def __str__(self) -> str:
        if self.href:
            return self._annotate_string(f"@Mention({self.plain_text})")

        return self._annotate_string(self.plain_text)

    def can_merge_with(self, other: Union[NotionRichText, NotionMention]) -> bool:
        base_matches = super(NotionMention, self).can_merge_with(other)
        if not base_matches:
            return False

        if not hasattr(other, "mention_type"):
            return False

        if self.mention_type != other.mention_type:
            return False

        return True


# {
#     "annotations": {
#         "bold": False,
#         "code": False,
#         "color": "default",
#         "italic": False,
#         "strikethrough": False,
#         "underline": False,
#     },
#     "href": None,
#     "mention": {"page": {"id": "UUID"}, "type": "page"},
#     "plain_text": "Gremgram",
#     "type": "mention",
# }


class NotionPageMention(NotionMention):
    def __init__(self, page_id: str = ""):
        super(NotionPageMention, self).__init__(text="Untitled")
        # self.href = f"https://www.notion.so/{page_id}" if page_id else href
        self._page_id = ""
        self.page_id = page_id

    @property
    def page_id(self) -> str:
        return self._page_id

    @page_id.setter
    def page_id(self, new_page_id: str):
        new_page_id = new_page_id.replace("-", "")
        self._page_id = new_page_id
        try:
            child_page_dict = client.CLIENT.get_block(new_page_id)
        except RuntimeError:
            print("Error: broken page_id '%s'" % new_page_id)
            self.plain_text = "BROKEN_LINK_{}".format(new_page_id)
            return

        page_title = child_page_dict[child_page_dict["type"]]["title"]
        self.plain_text = page_title

    def to_dict(self) -> Dict[str, str or Dict[str, str]]:
        new_dict = super(NotionPageMention, self).to_dict()
        new_dict["mention"] = {
            "page": {"id": self.page_id},
            "type": "page",
        }
        return new_dict

    @classmethod
    def from_dict(cls, data: Dict) -> NotionPageMention:
        page_id = ""

        # Page ID (if possible)
        if data.get("mention"):
            mention_type = data["mention"]["type"]
            page_id = data["mention"][mention_type]["id"]

        # Initial creation
        new_instance = cls(page_id=page_id)

        # Annotations
        _annotations = data["annotations"]
        if isinstance(_annotations, dict):
            _annotations = notion_annotations.NotionAnnotations.from_dict(_annotations)
        new_instance.annotations = _annotations

        return new_instance

    def __str__(self) -> str:
        return self._annotate_string(f"@Page({self.plain_text})")

    def can_merge_with(self, other: Union[NotionRichText, NotionMention, NotionPageMention]) -> bool:
        base_matches = super(NotionPageMention, self).can_merge_with(other)
        if not base_matches:
            return False

        return self.page_id == other.page_id


# {'annotations': {'bold': False,
#                   'code': False,
#                   'color': 'default',
#                   'italic': False,
#                   'strikethrough': False,
#                   'underline': False},
#   'href': None,
#   'mention': {'date': {'end': '2023-10-15T13:00:00.000-07:00',
#                        'start': '2023-10-14T13:00:00.000-07:00',
#                        'time_zone': None},
#               'type': 'date'},
#   'plain_text': '2023-10-14T13:00:00.000-07:00 → '
#                 '2023-10-15T13:00:00.000-07:00',
#   'type': 'mention'}]},


# Absolute
# '{'annotations': {'bold': False,
#                    'code': False,
#                    'color': 'default',
#                    'italic': False,
#                    'strikethrough': False,
#                    'underline': False},
#    'href': None,
#    'mention': {'date': {'end': '2023-10-15T13:00:00.000-07:00',
#                         'start': '2023-10-14T13:00:00.000-07:00',
#                         'time_zone': None},
#                'type': 'date'},
#    'plain_text': '2023-10-14T13:00:00.000-07:00 → '
#                  '2023-10-15T13:00:00.000-07:00',
#            'type': 'mention'}]},


class NotionDateMention(NotionMention):
    def __init__(self, start: str, end: str or None = None, time_zone: str or None = None):
        super(NotionDateMention, self).__init__(text="")
        self.start = start
        self.end = end
        self.time_zone = time_zone

    @property
    def mention_type(self):
        return "date"

    def to_dict(self) -> Dict[str, str or Dict[str, str]]:
        new_dict = super(NotionDateMention, self).to_dict()
        new_dict["mention"] = {
            self.mention_type: {
                "start": self.start,
                "end": self.end,
                "time_zone": self.time_zone,
            },
            "type": self.mention_type,
        }
        return new_dict

    @classmethod
    def from_dict(cls, data: Dict) -> NotionDateMention:
        start_date = None
        end_date = None
        time_zone = None

        # Page ID (if possible)
        if data.get("mention"):
            mention_type = data["mention"]["type"]
            date = data["mention"][mention_type]

            start_date = date["start"]
            end_date = date["end"]
            time_zone = date["time_zone"]

        # Initial creation
        new_instance = cls(start_date, end=end_date, time_zone=time_zone)

        # Plain text (temporary)
        # NOTE: This should be automatically managed with the start/end/time_zone data.
        new_instance.plain_text = data.get("plain_text", "")

        # Annotations
        _annotations = data["annotations"]
        if isinstance(_annotations, dict):
            _annotations = notion_annotations.NotionAnnotations.from_dict(_annotations)
        new_instance.annotations = _annotations

        return new_instance

    def __str__(self) -> str:
        return self._annotate_string(f"@Date({self.plain_text})")

    def can_merge_with(self, other: Union[NotionRichText, NotionMention, NotionDateMention]) -> bool:
        base_matches = super(NotionDateMention, self).can_merge_with(other)
        if not base_matches:
            return False

        return all([self.start == other.start, self.end == other.end, self.time_zone == other.time_zone])
