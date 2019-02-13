from PIL import Image
import requests
from io import BytesIO
from numpy import mean

from sklearn.cluster import KMeans
from collections import Counter
import cv2 #for resizing image
import numpy

def get_dominant_color(img, k=4, image_processing_size = None):
    w, h = img.size
    pixels = list(img.getdata())
    width, height = img.size
    pixels = numpy.array([pixels[i * width:(i + 1) * width] for i in xrange(height)])

    #make image list of "interesting" (non-grey) pixels
    pixels = pixels.reshape((pixels.shape[0] * pixels.shape[1], 3))
    pixels = [pixel for pixel in pixels if max(pixel) - min(pixel) > 25]

    #cluster and assign labels to the pixels
    clt = KMeans(n_clusters = k)
    labels = clt.fit_predict(pixels)

    #count labels to find most popular
    label_counts = Counter(labels)

    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return tuple(map(int, dominant_color))

artUrl = "https://open.spotify.com/image/f143aa84c6b879b2ad7662e292600908d742c83d"

response = requests.get(artUrl)
img = Image.open(BytesIO(response.content))

print(get_dominant_color(img))
