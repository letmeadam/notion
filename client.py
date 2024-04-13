import functools
import logging
import os
import time
from pprint import pprint, pformat
from typing import Callable, Dict, List, Union

import requests

PAGES_URL: str = "https://api.notion.com/v1/pages/"
BLOCKS_URL: str = "https://api.notion.com/v1/blocks/"


def get_page_url(page_id) -> str:
    return f"{PAGES_URL}{page_id}"


def get_block_url(block_id) -> str:
    return f"{BLOCKS_URL}{block_id}"


def get_block_children_url(block_id: str) -> str:
    return f"{BLOCKS_URL}{block_id}/children"


def retry_requests(retries: int = 3, sleep_amount: float = 10) -> Callable:
    def _retry_decorator(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            for _ in range(retries):
                try:
                    return func(*args, **kwargs)
                except RuntimeError:
                    logging.exception("Runtime error detected...")
                    time.sleep(sleep_amount)
            raise

        return _wrapper

    return _retry_decorator


_NOTION_SECRET: str = os.environ["NOTION_API_KEY"]


class NotionClient(object):
    __HEADERS: Dict[str, str] = {
        "Authorization": f"Bearer {_NOTION_SECRET}",
        "Content-Type": "application/json",
        "Notion-Version": "2022-06-28",
    }

    @retry_requests()
    def get_page(self, page_id: str) -> Dict[str, str or Dict]:
        pages_url = get_page_url(page_id)
        page_response = requests.get(pages_url, headers=self.__HEADERS)

        if page_response.status_code >= 400:
            message = f"GET response: {page_response.status_code}"
            logging.debug(message)
            # logging.debug(f"GET response: {page_response.status_code}")
            # print(f"GET response: {page_response.status_code}")
            logging.debug(pformat(page_response.json()))
            # pprint(page_response.json())
            raise RuntimeError(message)

        return page_response.json()

    @retry_requests()
    def add_page(self, page_data: Dict[str, str or Dict]) -> str:
        # parent_id: str, properties: dict[str: any]
        page_response = requests.post(PAGES_URL, json=page_data, headers=self.__HEADERS)
        if page_response.status_code >= 400:
            message = f"POST response: {page_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(page_response.json()))

            logging.debug("PAGE DATA:")
            logging.debug(pformat(page_data))
            raise RuntimeError(message)

        new_page_data = page_response.json()

        logging.info(f"Created page id: {new_page_data['id']}")
        return new_page_data["id"]

    @retry_requests()
    def patch_page(self, page_id: str, patch_data: Dict) -> None:
        if isinstance(page_id, dict):
            page_id = page_id["id"]

        page_url = get_page_url(page_id)
        page_response = requests.patch(page_url, json=patch_data, headers=self.__HEADERS)

        if page_response.status_code >= 400:
            message = f"PATCH response: {page_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(page_response.json()))
            # print(f"PATCH response: {page_response.status_code}")
            # pprint(page_response.json())

            logging.debug("PAGE DATA:")
            logging.debug(pformat(patch_data))
            # print("\nPATCH DATA:")
            # pprint(patch_data)
            raise RuntimeError(message)

    @retry_requests()
    def delete_page(self, page_id: str) -> None:
        if isinstance(page_id, dict):
            page_id = page_id["id"]

        pages_url = get_page_url(page_id)
        patch_data = {
            # "page_id": page_id,
            "archived": True,
        }
        page_response = requests.patch(pages_url, json=patch_data, headers=self.__HEADERS)

        if page_response.status_code >= 400:
            message = f"PATCH response: {page_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(page_response.json()))

            logging.debug("PAGE DATA:")
            logging.debug(pformat(patch_data))
            raise RuntimeError(message)

    @retry_requests()
    def restore_page(self, page_id: str) -> None:
        if isinstance(page_id, dict):
            page_id = page_id["id"]

        pages_url = get_page_url(page_id)
        patch_data = {
            "archived": False,
        }
        page_response = requests.patch(pages_url, json=patch_data, headers=self.__HEADERS)

        if page_response.status_code >= 400:
            message = f"PATCH response: {page_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(page_response.json()))

            logging.debug("PAGE DATA:")
            logging.debug(pformat(patch_data))
            raise RuntimeError(message)

    @retry_requests()
    def get_block(self, block_id: str) -> Dict:
        blocks_url = get_block_url(block_id)
        blocks_response = requests.get(blocks_url, headers=self.__HEADERS)

        if blocks_response.status_code >= 400:
            message = f"GET response: {blocks_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(blocks_response.json()))
            # print(f"GET response: {blocks_response.status_code}")
            # pprint(blocks_response.json())
            raise RuntimeError(message)

        return blocks_response.json()

    @retry_requests()
    def get_block_children(self, block_id: str) -> Union[List, Dict]:
        blocks_url = get_block_children_url(block_id)
        blocks_response = requests.get(blocks_url, headers=self.__HEADERS)

        if blocks_response.status_code >= 400:
            message = f"GET response: {blocks_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(blocks_response.json()))

            # print(f"GET response: {blocks_response.status_code}")
            # pprint(blocks_response.json())
            raise RuntimeError(message)

        blocks_data = blocks_response.json()
        blocks = blocks_data["results"]

        return blocks

    @retry_requests()
    def patch_block(self, block_id: str, patch_data: Dict, append: bool = False) -> Dict:
        if isinstance(block_id, dict):
            block_id = block_id["id"]

        blocks_url = get_block_url(block_id)
        if append:
            blocks_url = get_block_children_url(block_id)

        blocks_response = requests.patch(blocks_url, json=patch_data, headers=self.__HEADERS)

        if blocks_response.status_code >= 400:
            message = f"PATCH response: {blocks_response.status_code}"
            logging.debug(message)
            logging.debug(pformat(blocks_response.json()))

            # pprint(blocks_response.json())
            #
            logging.debug("PATCH DATA:")
            logging.debug(pformat(patch_data))
            # print("\nPATCH DATA:")
            # pprint(patch_data)
            raise RuntimeError(message)

        return blocks_response.json()

    @retry_requests()
    def delete_block(self, block_id: str) -> None:
        if isinstance(block_id, dict):
            block_id = block_id["id"]

        blocks_url = get_block_url(block_id)
        blocks_response = requests.delete(blocks_url, headers=self.__HEADERS)

        if blocks_response.status_code >= 400:
            message = f"DELETE response: {blocks_response.status_code}"
            pprint(blocks_response.json())

            print("\nDELETE DATA:")
            pprint(block_id)
            raise RuntimeError(message)


CLIENT: NotionClient = NotionClient()
