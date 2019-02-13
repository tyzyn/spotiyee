import subprocess
import re
import time
from PIL import Image
import requests
from io import BytesIO
from change_colour import set_color, set_bright
import numpy
from sklearn.cluster import KMeans
from collections import Counter

def get_song():

    #get current playing song and return the dictionary in string form
    track = subprocess.check_output(["dbus-send", "--print-reply",
                               "--dest=org.mpris.MediaPlayer2.spotify",
                               "/org/mpris/MediaPlayer2",
                               "org.freedesktop.DBus.Properties.Get",
                               "string:org.mpris.MediaPlayer2.Player",
                               "string:Metadata"])

    track = track.decode('utf-8')
    track_details = dict()
    entry = []
    entry_count = 0
    key = ""

    for line in track.split('\n'):
        if "entry" in line:
            entry = []
            entry_count = 1

        elif line.strip() == ")":
            track_details[key] = entry
            entry_count = 0

        elif entry_count == 1:
            key = line.split(':')[-1][:-1]
            entry_count += 1

        elif entry_count > 1:
            if "string" in line:
                entry.append(re.findall('"([^"]*)"', line)[0])
            elif "variant" in line and "array" not in line:
                entry.append(line.split()[-1])
            entry_count += 1

    return track_details

def get_album_colour(artUrl):
    response = requests.get(artUrl)
    img = Image.open(BytesIO(response.content))

    w, h = img.size
    pixels = list(img.getdata())
    width, height = img.size
    pixels = numpy.array([pixels[i * width:(i + 1) * width] for i in xrange(height)])

    #make image list of "interesting" (non-grey) pixels
    def interesting_pixel(pixel):
        #pixel is too grey
        too_grey = max(pixel) - min(pixel) < 70
        #pixel is too white
        too_white = min(pixel) > 180
        #pixel is too black
        too_black = max(pixel) < 70

        return not(too_grey or too_white or too_black)

    pixels = pixels.reshape((pixels.shape[0] * pixels.shape[1], 3))
    pixels = [pixel for pixel in pixels if interesting_pixel(pixel)]

    if not pixels:
        return

    #cluster and assign labels to the pixels
    clt = KMeans(n_clusters = 3)
    labels = clt.fit_predict(pixels)

    #count labels to find most popular
    label_counts = Counter(labels)

    def grab_colour(x):
        dominant_color = clt.cluster_centers_[label_counts.most_common(3)[x][0]]
        dominant_color[numpy.argmax(dominant_color)] *= 1.2
        if dominant_color[numpy.argmax(dominant_color)] > 255:
            dominant_color[numpy.argmax(dominant_color)] = 255
        dominant_color = tuple(map(int, dominant_color))

        rgb_string = '#%02x%02x%02x' % dominant_color
        print(rgb_string)
        return rgb_string[1:]

    return grab_colour(0), grab_colour(1)

if __name__ == "__main__":
		song_title = ""
		set_bright(1, 20)
		set_bright(1, 20)
		while True:
				details = get_song()
				if details["title"][0] != song_title:
				    song_title = details["title"][0]
				    album_art = details["artUrl"][0]
				    print(song_title)
				    print(album_art + "\n")
				    cols = get_album_colour(album_art)
				    if cols:
				        col1, col2 = cols
				        set_color(1, col1)
				        set_color(2, col2)
				        time.sleep(0.5)
