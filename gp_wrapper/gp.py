from typing import Optional, Generator, Iterable
import requests
from requests.models import Response
from danielutils import warning, threadify
from google.oauth2.credentials import Credentials  # type:ignore
from google_auth_oauthlib.flow import InstalledAppFlow  # type:ignore
# from googleapiclient.discovery import Resource  # type:ignore
# import googleapiclient.discovery  # type:ignore
from .media_item import GooglePhotosMediaItem
from .album import GooglePhotosAlbum
from .utils import UploadToken, Url, Path, declare, split_iterable
from .pool_executor import ThreadPoolExecutor
SCOPES = [
    'https://www.googleapis.com/auth/photoslibrary',
    "https://www.googleapis.com/auth/photoslibrary.appendonly",
    "https://www.googleapis.com/auth/photoslibrary.sharing",
    "https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata"
]
EMPTY_PROMPT_MESSAGE = ""
DEFAULT_NUM_WORKERS: int = 2


class GooglePhotos:
    """A wrapper class over GooglePhotos API to get 
    higher level abstraction for easy use
    """
    ALBUMS_ENDPOINT = "https://photoslibrary.googleapis.com/v1/albums"
    UPLOAD_MEDIA_ITEM_ENDPOINT = "https://photoslibrary.googleapis.com/v1/uploads"
    CREATE_ENDPOINT = "https://photoslibrary.googleapis.com/v1/mediaItems:batchCreate"

    @declare("Initializing Google Photos service")
    def __init__(self, client_secrets_path: str = "./client_secrets.json") -> None:
        flow: InstalledAppFlow = InstalledAppFlow.from_client_secrets_file(client_secrets_path, SCOPES)  # noqa
        self.credentials: Credentials = flow.run_local_server(
            port=0,
            authorization_prompt_message=EMPTY_PROMPT_MESSAGE
        )
        self.session = requests.Session()
        self.session.credentials = self.credentials  # type:ignore

    def get(self, endpoint: Url, *args, **kwargs) -> Response:
        """wrapper function to create general purpose GET request with the current session

        Args:
            endpoint (Url): the endpoint to call

        Returns:
            Response: the response of the request
        """
        return self.session.get(endpoint, *args, **kwargs)

    def post(self, endpoint: Url, *args, **kwargs) -> Response:
        """wrapper function to create general purpose POST request with the current session

        Args:
            endpoint (Url): the endpoint to call

        Returns:
            Response: the response of the request
        """
        return self.session.post(endpoint, *args, **kwargs)

    def _construct_headers(self, additional_headers: Optional[dict] = None) -> dict:
        BASE_HEADERS: dict = {
            "Authorization": f"Bearer {self.credentials.token}"}
        res = dict(BASE_HEADERS)
        if additional_headers is not None:
            res.update(additional_headers)
        return res

    def json_headers(self) -> dict:
        return self._construct_headers({"Content-Type": "application/json"})

    @declare("Creating an Album")
    def create_album(self, album_name: str) -> GooglePhotosAlbum:
        headers = self.json_headers()
        payload = {
            "album": {
                "title": album_name
            }
        }
        response = self.post(
            GooglePhotos.ALBUMS_ENDPOINT,
            json=payload,
            headers=headers
        )
        dct = response.json()
        album = GooglePhotosAlbum.from_dict(self, dct)
        return album

    @declare
    def _upload_media_item(self, media_path: Path) -> UploadToken:
        headers = self.json_headers()
        image_data = open(media_path, 'rb').read()
        response = self.post(
            GooglePhotos.UPLOAD_MEDIA_ITEM_ENDPOINT,
            data=image_data,
            headers=headers
        )
        token = response.content.decode('utf-8')
        return token

    @declare
    def _get_media_item_id(self, upload_token: UploadToken) -> GooglePhotosMediaItem:
        headers = self._construct_headers()
        create_payload = {
            "newMediaItems": [
                {
                    "simpleMediaItem": {
                        "uploadToken": upload_token
                    }
                }
            ]
        }
        response = self.post(
            GooglePhotos.CREATE_ENDPOINT,
            json=create_payload,
            headers=headers
        )
        dct = response.json()['newMediaItemResults'][0]['mediaItem']
        return GooglePhotosMediaItem(
            self,
            id=dct["id"],
            productUrl=dct["productUrl"],
            mimeType=dct["mimeType"],
            mediaMetadata=dct["mediaMetadata"],
            filename=dct["filename"],
        )

    @declare("Uploading media to Album")
    def upload_media(self, album: GooglePhotosAlbum, media_path: Path) -> dict:
        """uploads a single image into an album

        Args:
            album (GooglePhotosAlbum): the album wrapper object
            media_path (Path): the path to the image

        Returns:
            dict: the result of the request. empty dict means success
        """
        media = self._get_media_item_id(self._upload_media_item(media_path))
        endpoint = f"https://photoslibrary.googleapis.com/v1/albums/{album.id}:batchAddMediaItems"
        headers = self._construct_headers()
        response = self.post(
            endpoint, headers=headers,
            json={
                "mediaItemIds": [media.id]
            }
        )
        return response.json()

    @declare("Uploading images in batches")
    def upload_media_batch(self, album: GooglePhotosAlbum, paths: Iterable[Path],
                           num_workers: int = DEFAULT_NUM_WORKERS) -> tuple[Iterable[Response], Iterable[GooglePhotosMediaItem]]:
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
                    self._upload_media_item(path))
                all_media.append(media)
                media_ids.append(media.id)
            headers = self._construct_headers()
            response = self.post(
                endpoint, headers=headers,
                json={
                    "mediaItemIds": media_ids
                }
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
