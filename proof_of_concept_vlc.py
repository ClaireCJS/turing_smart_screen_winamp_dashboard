import requests

vlc_lua_port   = "8080"                                                 # Replace 'localhost' and '8080' with your VLC server IP and port if different
vlc_ip_address = "localhost"                                            # Replace 'localhost' and '8080' with your VLC server IP and port if different
url = f"http://{vlc_ip_address}:{vlc_lua_port}/requests/status.json"
print(f"* vlc control URL is {url}")

# If you set a password, use HTTP Basic Authentication
auth = ('', 'winampdashboard')  # (username, password), leave username as empty string

response = requests.get(url, auth=auth)

if response.status_code == 200:
    # The response will contain JSON data with the status of VLC
    status = response.json()
    print(status)

    # Extracting specific values
    show_name = status.get('info', {}).get('title', 'Unknown')
    video_resolution = status.get('video', {}).get('width', 'Unknown'), status.get('video', {}).get('height', 'Unknown')
    frame_rate = status.get('video', {}).get('fps', 'Unknown')
    codec = status.get('info', {}).get('codec', 'Unknown')
    language = status.get('info', {}).get('language', 'Unknown')
    position = status.get('position', 'Unknown')

else:
    print(f"Failed to connect to VLC. Status code: {response.status_code}")

 # Extracting specific values
    show_name = status.get('info', {}).get('title', 'Unknown')
    video_resolution = status.get('video', {}).get('width', 'Unknown'), status.get('video', {}).get('height', 'Unknown')
    frame_rate = status.get('video', {}).get('fps', 'Unknown')
    codec = status.get('info', {}).get('codec', 'Unknown')
    language = status.get('info', {}).get('language', 'Unknown')
    position = status.get('position', 'Unknown')

    print(f"Show Name: {show_name}")
    print(f"Video Resolution: {video_resolution[0]}x{video_resolution[1]}")
    print(f"Frame Rate: {frame_rate} fps")
    print(f"Codec: {codec}")
    print(f"Language: {language}")
    print(f"Position: {position}")
