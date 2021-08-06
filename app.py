# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)

UPLOAD_FOLDER = './static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    img_name = ""
    if request.method == 'POST':
        img_file = request.files['image']
        N_cols = request.form['name']
        filename = secure_filename(img_file.filename)
        img_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        img_file.save(img_url)
        print("img uploaded")
    if request.method == 'GET':
        print("get")
    return render_template('index.html', img_name=img_name)



if __name__ == '__main__':
    app.debug = True
    app.run()