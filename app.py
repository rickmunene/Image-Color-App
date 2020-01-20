# web-app for API image manipulation

from flask import Flask, request, render_template, send_from_directory
import os
from PIL import Image
import cv2
import sys
import requests
import pandas as pd
import requests
import re
import json
import os


app = Flask(__name__)
app.config["CACHE_TYPE"] = "null"
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

APP_ROOT = os.path.dirname(os.path.abspath(__file__))


# default access page
@app.route("/")
def main():
    return render_template('index.html')


# upload selected image and forward to processing page
@app.route("/upload", methods=["POST"])
def upload():
    target = os.path.join(APP_ROOT, 'tmp')

    # create image directory if not found
    if not os.path.isdir(target):
        os.mkdir(target)

    # retrieve file from html file-picker
    upload = request.files.getlist("file")[0]
    print("File name: {}".format(upload.filename))
    filename = upload.filename

    # file support verification
    ext = os.path.splitext(filename)[1]
    if (ext == ".jpg") or (ext == ".png") or (ext == ".bmp") or (ext == ".PNG") or (ext == ".JPG"):
        print("File accepted")
    else:
        return render_template("error.html", message="The selected file is not supported"), 400

    # save file
    destination = "/".join([target, filename])
    print("File saved to to:", destination)
    upload.save(destination)

    # forward to processing page
    return render_template("processing.html", image_name=filename)


# change image 'color'
@app.route("/color", methods=["POST"])
def color():
    filename = request.form['image']

    # open and process image
    target = os.path.join(APP_ROOT, 'tmp')
    destination = "/".join([target, filename])

    img = Image.open(destination)

    # save and return image
    destination = "/".join([target, 'temp.png'])
    if os.path.isfile(destination):
        os.remove(destination)
    img.save(destination)

    res = requests.post("https://api.deepai.org/api/colorizer",
                        files={'image': open(destination, 'rb'), },
                        headers={'api-key': 'change-key'})

    url = res.json()['output_url']

    # Open and read the txt file with json url

    destination2 = "/".join([target, 'temp2.png'])

    print(url)
    result = requests.get(url, stream=True)
    if result.status_code == 200:
        image = result.raw.read()
        open(os.path.join(destination2), "wb").write(image)

    return render_template("post-processing.html", image_name="temp2.png")


# retrieve file from 'tmp' directory
@app.route('/tmp/<filename>')
def send_image(filename):
    return send_from_directory("tmp", filename)


if __name__ == "__main__":
    app.run()
