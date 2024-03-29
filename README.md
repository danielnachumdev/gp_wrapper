# gp_wrapper v=0.9.8
A Google Photos API wrapper library

* Official API is already supported

## What does this package offer?
Support for all of the official API and more convenience function as well.
A-lot of well defined API inspired Classes and Enums to simplify the usage.
* `GooglePhotos` class - wrapper over authenticated HTTP session
* `Album` Class - handles all of the global and instance methods for an Album
* `MediaItem` Class - handles all of the global and instance methods for MediaItem
* Enums: `RequestType`, `HeaderType`, `MimeType`, `PositionType`, `EnrichmentType`, `MediaItemMaskTypes`, `AlbumMaskType`, `RelativeItemType`, `StatusCode`
* Classes: `SimpleMediaItem`, `NewMediaItem`, `AlbumPosition`, `Status`, `MediaItemResult`, `MediaMetadata`, `ContributorInfo`
## Quick Start
1. Create a [Google Cloud Console](https://console.cloud.google.com/) project
2. Enable google photos API [here](https://console.cloud.google.com/apis/library/photoslibrary.googleapis.com)
3. Fill information [here](https://console.cloud.google.com/apis/credentials/consent)
    1.  Fill application name and detail
    2. Apply scopes
        1. https://www.googleapis.com/auth/photoslibrary,
        2. https://www.googleapis.com/auth/photoslibrary.appendonly
        3. https://www.googleapis.com/auth/photoslibrary.sharing
        4. https://www.googleapis.com/auth/photoslibrary.edit.appcreateddata
    3. Add a google account as a Test User which will be able to use you project as an 'end user'
3. Extract relevant data for [`client_secrets.json`](./READMES/client_secrets_example.json)
2. `pip install gp_wrapper`
3. See example [here](./READMES/example.md)