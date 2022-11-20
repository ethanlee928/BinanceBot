from __future__ import annotations
import os
import requests
from enum import Enum
from typing import Dict, Any

from utils import logger

TOKEN = "Bearer " + os.getenv("SLACK_TOKEN")


class UndefinedAPIError(Exception):
    """Raised when API is undefined"""

    ...


class MissingBodyError(Exception):
    """Raised when some information in body is missing"""

    ...


class SlackRequest:
    class API(Enum):
        _BASE = "https://slack.com/api/"

        POST_MESSAGE = _BASE + "chat.postMessage"
        UPLOAD_FILE = _BASE + "files.upload"

    def __init__(self, api: API, headers: Dict[str, str], body: Dict[str, Any]) -> None:
        self.api = api
        self.headers = headers
        self.body = body

    def post_request(self):
        match self.api:
            case self.API.POST_MESSAGE:
                return self._post_message()
            case self.API.UPLOAD_FILE:
                return self._upload_file()
            case _:
                raise UndefinedAPIError("API is undefined")

    def _post_message(self):
        data = self.body.get("data")
        if data:
            logger.info(f"Posting message: {data}")
            return requests.post(self.api.value, headers=self.headers, data=data)
        else:
            raise MissingBodyError(f"Missing data in body for posting message")

    def _upload_file(self):
        files = self.body.get("files")
        data = self.body.get("data")
        if files and data:
            logger.info(f"Uploading file: {files}, data: {data}")
            return requests.post(self.api.value, headers=self.headers, data=data, files=files)
        else:
            raise MissingBodyError(f"Missing files or data in body for uploading file")

    @staticmethod
    def create_msg_request(channel: str, msg: str) -> SlackRequest:
        headers = dict(Authorization=TOKEN)
        data = dict(channel=channel, text=msg)
        body = dict(data=data)
        return SlackRequest(api=SlackRequest.API.POST_MESSAGE, headers=headers, body=body)

    @staticmethod
    def create_upload_file_request(channel: str, file_path: str) -> SlackRequest:
        headers = dict(Authorization=TOKEN)
        data = dict(channels=channel)
        files = dict(file=open(file_path, "rb"))
        body = dict(data=data, files=files)
        return SlackRequest(api=SlackRequest.API.UPLOAD_FILE, headers=headers, body=body)
