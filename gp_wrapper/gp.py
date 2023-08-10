import json
from typing import Optional, Iterable, Callable
import requests
from requests.models import Response
from danielutils import warning
from google.oauth2.credentials import Credentials  # type:ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type:ignore
from .media_item import GPMediaItem
from .album import GPAlbum
from .structures import Path, RequestType, Printable,\
    EMPTY_PROMPT_MESSAGE, SCOPES, MEDIA_ITEMS_CREATE_ENDPOINT, DEFAULT_NUM_WORKERS
from .helpers import split_iterable


class GooglePhotos(Printable):
    """A wrapper class over GooglePhotos API to get 
    higher level abstraction for easy use
    """

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

    def _get_media_item_id(self, upload_token: str) -> GPMediaItem:
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
            return GPMediaItem.from_dict(self, dct)

        print(json.dumps(j, indent=4))
        raise AttributeError("'newMediaItemResults' not found in response")

    def upload_media(self, album: GPAlbum, media_path: Path) -> dict:
        """uploads a single image into an album

        Args:
            album (GooglePhotosAlbum): the album wrapper object
            media_path (Path): the path to the image

        Returns:
            dict: the result of the request. empty dict means success
        """
        media = self._get_media_item_id(
            GPMediaItem.upload_media(self, media_path))
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album.id}:batchAddMediaItems"
        payload = {
            "mediaItemIds": [media.id]
        }
        response = self.request(
            RequestType.POST,
            endpoint,
            json=payload
        )
        return response.json()

    def upload_media_batch(self, album: GPAlbum, paths: Iterable[Path],
                           num_workers: int = DEFAULT_NUM_WORKERS) -> tuple[Iterable[Response], Iterable[GPMediaItem]]:
        """uploads media in batches of 50 images at once
        Args:
            album (GooglePhotosAlbum): the album wrapper object
            paths (Iterable[Path]): the iterable which has the paths to the media

        Yields:
            Generator[dict, None, None]: yields the results of each batch request. empty dict means success
        """
        # see https://developers.google.com/photos/library/reference/rest/v1/albums/batchAddMediaItems#request-body
        MAX_SIZE: int = 50
        if not (0 < num_workers <= MAX_SIZE):
            warning(
                f"Invalid value for number of workers, using {DEFAULT_NUM_WORKERS=}")
            num_workers = DEFAULT_NUM_WORKERS
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album.id}:batchAddMediaItems"
        all_media = []
        responses = []

        def worker(batch: list[str]):
            media_ids = []
            for path in batch:
                media = self._get_media_item_id(
                    GPMediaItem.upload_media(self, path))
                all_media.append(media)
                media_ids.append(media.id)
            headers = self._construct_headers()
            payload = {
                "mediaItemIds": media_ids
            }
            response = self.request(
                RequestType.POST,
                endpoint, headers=headers,
                json=payload
            )
            responses.append(response)
        for batch in split_iterable(paths, MAX_SIZE):
            worker(batch)
        # ====== NEED TO FIND HOW TO ENABLE THIS ======
        # pool = ThreadPoolExecutor(num_workers, worker)
        # for batch in split_iterable(paths, MAX_SIZE):
        #     pool.submit((batch,))
        # pool.run()
        return responses, all_media

    # def delete_album(self, album: GooglePhotosAlbum) -> Response:
    #     raise NotImplementedError(
    #         "The Google API does not support deleting albums")
    #     ALBUM_DELETE_ENDPOINT = f"https://photoslibrary.googleapis.com/v1/albums/{album.id}"
    #     headers = self.json_headers()
    #     response = self.session.delete(ALBUM_DELETE_ENDPOINT, headers=headers)
    #     return response


__all__ = [
    "GooglePhotos"
]
