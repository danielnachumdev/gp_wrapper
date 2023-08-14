import json
from typing import Optional,  Callable
import requests
from requests.models import Response
from google.oauth2.credentials import Credentials  # type:ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type:ignore
# type:ignore #noqa # pylint: disable=import-error
import gp_wrapper.objects.core.media_item
from ...utils import RequestType, Printable, EMPTY_PROMPT_MESSAGE, SCOPES, MEDIA_ITEMS_CREATE_ENDPOINT


class CoreGooglePhotos(Printable):
    """A wrapper class over GooglePhotos API to get 
    higher level abstraction for easy use
    """
    # TODO implement quota

    def __init__(self, client_secrets_path: str = "./client_secrets.json", quota: int = 30) -> None:
        flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)  # noqa
        self.credentials: Credentials = flow.run_local_server(
            port=0,
            authorization_prompt_message=EMPTY_PROMPT_MESSAGE
        )
        self.session = requests.Session()
        self.session.credentials = self.credentials  # type:ignore

    def request(self, req_type: RequestType, endpoint: str, *args, use_json_headers: bool = True, **kwargs) -> Response:
        if use_json_headers:
            headers = self._json_headers()
        else:
            headers = self._construct_headers()
        request_map: dict[RequestType, Callable[..., Response]] = {
            RequestType.GET: self.session.get,
            RequestType.POST: self.session.post,
            RequestType.PATCH: self.session.patch,
        }
        return request_map[req_type](url=endpoint, headers=headers, *args, **kwargs)

    def _construct_headers(self, additional_headers: Optional[dict] = None) -> dict:
        BASE_HEADERS: dict = {
            "Authorization": f"Bearer {self.credentials.token}"}
        res = dict(BASE_HEADERS)
        if additional_headers is not None:
            res.update(additional_headers)
        return res

    def _json_headers(self) -> dict:
        return self._construct_headers({"Content-Type": "application/json"})

    def _get_media_item_id(self, upload_token: str) -> "gp_wrapper.objects.core.media_item.CoreGPMediaItem":
        payload = {
            "newMediaItems": [
                {
                    "simpleMediaItem": {
                        "uploadToken": upload_token
                    }
                }
            ]
        }
        response = self.request(
            RequestType.POST,
            MEDIA_ITEMS_CREATE_ENDPOINT,
            json=payload,
            use_json_headers=False
        )
        j = response.json()
        if "newMediaItemResults" in j:
            dct = j['newMediaItemResults'][0]['mediaItem']
            return gp_wrapper.objects.core.media_item.CoreGPMediaItem.from_dict(self, dct)

        # TODO fix this
        print(json.dumps(j, indent=4))
        raise AttributeError("'newMediaItemResults' not found in response")


__all__ = [
    "CoreGooglePhotos"
]
