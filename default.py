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
    # Set plugin content type
    xbmcplugin.setContent(addon_handle, 'videos')

    try:
        # Send a request to the server using the provided URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        json_data = response.json()
        videos = json_data.get('data', [])  # Extract the 'data' array from the JSON

        # Add each video to the Kodi directory
        for video in videos:
            title = video.get('title', 'Unknown Title')
            image_url = video.get('imageUrl', '')
            description = video.get('description', 'No description available')                        
            rating = video.get('rating', 0)            
            

            list_item = xbmcgui.ListItem(label=title)
            list_item.setArt({'thumb': image_url, 'icon': image_url, 'fanart': image_url})

            # Create an InfoTagVideo object to set detailed video info
            info_tag = list_item.getVideoInfoTag()
            info_tag.setTitle(title)
            info_tag.setPlot(description)                        
            try:
                info_tag.setRating(float(rating))
            except ValueError:
                info_tag.setRating(0.0)  # Set a default rating if conversion fails
       

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

    # Signal the end of directory listing
    xbmcplugin.endOfDirectory(addon_handle)


def play_video(video_path):
    play_item = xbmcgui.ListItem(path=video_path)    
    xbmcplugin.setResolvedUrl(addon_handle, True, listitem=play_item)


def router(paramstring):
    params = dict(parse_qsl(paramstring))
    status = params.pop('status', None)
    href = params.pop('href', None)

    # If 'page' is present, append it to the href
    page = params.pop('page', None)
    if page:
        if href:
            if '?' in href:
                href += '&' + urlencode({'page': page})
            else:
                href += '?' + urlencode({'page': page})

    if href:
        print("Status Length:", len(status) if status else 0)  # Print the length of the status if it exists

        if status == 'playable':
            play_video(href)

        elif status == 'playable1':
            try:
                response = requests.get(href)
                response.raise_for_status()
                json_data = response.json()
                videos = json_data.get('data', [])
                if videos:
                    play_url = videos[0].get('href', '')
                    list_item = xbmcgui.ListItem(label=videos[0].get('title', 'Unknown Title'))
                    list_item.setProperty('IsPlayable', 'true')
                    play_video(play_url)
                else:
                    print("No videos found")
            except requests.RequestException as e:
                print(f"Error fetching video data: {e}")

        elif status == 'browse':
            list_videos(href)
    else:
        initial_url = "http://192.168.1.100:4000/tv"
        list_videos(initial_url)

if __name__ == '__main__':
    addon = xbmcaddon.Addon()
    addon_handle = int(sys.argv[1])
    router(sys.argv[2][1:])  # Pass the parameter string to the router function
