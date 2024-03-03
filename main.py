import requests, random, string, ffmpeg
from transfersh_client.app import send_to_transfersh
import urllib.parse
import pyperclip
from pymediainfo import MediaInfo
from tkinter import filedialog
from tkinter import Tk
import sys

def generate_thumbnail(in_filename, out_filename):
    probe = ffmpeg.probe(in_filename)
    time = float(probe['streams'][0]['duration']) // 2
    width = probe['streams'][0]['width']
    try:
        (
            ffmpeg
            .input(in_filename, ss=time)
            .filter('scale', width, -1)
            .output(out_filename, vframes=1)
            .overwrite_output()
            .run(capture_stdout=True, capture_stderr=True)
        )
    except ffmpeg.Error as e:
        print(e.stderr.decode(), file=sys.stderr)
        sys.exit(1)

def generate_filename():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))

# Open file dialog
root = Tk()
root.withdraw()
video_path = filedialog.askopenfilename()
print("Selected video: " + video_path)

video_res = [0, 0]

media_info = MediaInfo.parse(video_path)
for track in media_info.tracks:
    if track.track_type == 'Video':
        video_res[0] = track.width
        video_res[1] = track.height
        print("Video resolution: " + str(track.width) + "x" + str(track.height))
        break

filename = generate_filename()

print("Generating thumbnail...")
generate_thumbnail(video_path, "thumbnail.jpg")

# Upload video to transfer.sh
print("Uploading video to transfer.sh...")
video_url = send_to_transfersh(video_path, clipboard=False)

print("Uploading thumbnail...")
url = 'https://autocompressor.net/av1/mkthumbnail'

# Form data:
# w: 1920
# h: 1200
# imgupload: (binary)

files = {
    'w': (None, str(video_res[0])),
    'h': (None, str(video_res[1])),
    'imgupload': open('thumbnail.jpg', 'rb')
}

thumbnail_url = requests.post(url, files=files).json()['imgUrl']

print("Thumbnail URL: " + thumbnail_url)
print("Video URL: " + video_url)

# Generate final URL
# Format: https://autocompressor.net/av1?v= (url encoded video url) &i= (url encoded thumbnail url) &w= (video width) &h= (video height)
final_url = "https://autocompressor.net/av1?v=" + urllib.parse.quote(video_url) + "&i=" + urllib.parse.quote(thumbnail_url) + "&w=" + str(video_res[0]) + "&h=" + str(video_res[1])
# short_url = requests.get("https://is.gd/create.php?format=simple&url=" + final_url).text

print("Final URL: " + final_url)
pyperclip.copy(final_url)