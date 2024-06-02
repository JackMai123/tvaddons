import sys
import xbmcplugin
import xbmcgui
import xbmcaddon
import requests
from urllib.parse import urlencode, parse_qsl

# import web_pdb; web_pdb.set_trace()

# Get the plugin url in plugin:// notation.
_URL = sys.argv[0]


def list_videos(url):

    # Set plugin category. It is displayed in some skins as the name
    # of the current section.
     # Set plugin content. It allows Kodi to select appropriate views
    # for this type of content.
    xbmcplugin.setContent(addon_handle, 'videos')

    try:
        # Send a request to the server using the provided URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        json_data = response.json()
        videos = json_data.get('data', [])  # Extract the 'data' array from the JSON

        # Add each video to the Kodi directory
        for video in videos:
            list_item = xbmcgui.ListItem(label=video.get('title', 'Unknown Title'))
            list_item.setArt({
                'thumb': video.get('imageUrl', ''),
                'icon': video.get('imageUrl', ''),
                'fanart': video.get('imageUrl', '')
            })
            list_item.setInfo('video', {'title': video.get('title', 'Unknown Title'),'mediatype': 'video'})

            # Check if the video is playable or browsable
            status = video.get('status')
            if status == 'playable':
                # If the status is "playable", add a playable URL
                play_url = video.get('href', '')
                list_item.setPath(play_url)
                list_item.setProperty('IsPlayable', 'true')
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=f"{_URL}?status=playable&href={play_url}", listitem=list_item, isFolder=False)
            elif status == 'playable1':
                play_url = video.get('href', '')
                list_item.setPath(play_url)
                list_item.setProperty('IsPlayable', 'true') 
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=f"{_URL}?status=playable1&href={play_url}", listitem=list_item, isFolder=False)
    
            else:
                # If the status is not "playable", add a browsable URL
                browse_url = video.get('href', '')
                xbmcplugin.addDirectoryItem(handle=addon_handle, url=f"{_URL}?status=browse&href={browse_url}", listitem=list_item, isFolder=True)

    except requests.RequestException as e:
        # Handle request errors
        xbmcgui.Dialog().ok('Error', f'Failed to fetch videos: {e}')


    # Add a sort method for the virtual folder items (alphabetically, ignore articles)
    # xbmcplugin.addSortMethod(addon_handle, xbmcplugin.SORT_METHOD_LABEL_IGNORE_THE)

    # Signal the end of directory listing
    xbmcplugin.endOfDirectory(addon_handle)


def play_video(video_path):
    play_item = xbmcgui.ListItem(path=video_path)    
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    if params:
        if params.get('status') == 'playable':
            video_path = params['href']
            play_video(video_path)
        elif params.get('status') == 'playable1':
            # If the user clicked on a browsable item, navigate to the provided URL and list videos
            browse_url = params['href']        
            response = requests.get(browse_url)
            response.raise_for_status()  # Raise an exception for bad status codes
            json_data = response.json()
            videos = json_data.get('data', [])  # Extract the 'data' array from the JSON
            play_url = videos[0].get('href', '')
            list_item = xbmcgui.ListItem(label=videos[0].get('title', 'Unknown Title'))
            list_item.setProperty('IsPlayable', 'true')
            play_video(play_url)

        elif params.get('status') == 'browse':
            # If the user clicked on a browsable item, navigate to the provided URL and list videos
            browse_url = params['href']
            list_videos(browse_url)
    else:
        # If no action specified, list initial videos
        initial_url = "http://192.168.1.100:4000/tv"  # Initial URL to fetch videos
        list_videos(initial_url)


if __name__ == '__main__':
    addon = xbmcaddon.Addon()
    addon_handle = int(sys.argv[1])
    router(sys.argv[2][1:])  # Pass the parameter string to the router function
