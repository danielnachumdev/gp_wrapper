from danielutils import get_files
from gp_wrapper import GooglePhotos, Album, MediaItem, SimpleMediaItem, NewMediaItem

gp = GooglePhotos()
DATA = "./DATA"


def main_test():
    album = Album.exists(gp, name="pytest")
    if not album:
        album = Album.create(gp, "pytest")
    album.upload_and_add((f"{DATA}/{f}" for f in get_files(DATA)))
