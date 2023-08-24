# gp_wrapper v=0.9.1
A Google Photos API wrapper library

currently a work in progress.

The target is to have all of the [official API](https://developers.google.com/photos/library/reference/rest) implemented and working in addition to convenience methods to simplify usage

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
3. Extract relevant data for [`client_secrets.json`](./READMES/client_secrets_example.json)
2. `pip install gp_wrapper`
3. See example [here](./READMES/example.md)