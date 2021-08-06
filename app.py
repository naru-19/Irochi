# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
app = Flask(__name__, static_url_path="")

UPLOAD_FOLDER = './static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_object(__name__)

cols=["r","g","b"]

IMG_DIR = "/static/images/"
CSV_DIR = "/static/csv/"
BASE_DIR = os.path.dirname(__file__)
IMG_PATH = BASE_DIR + IMG_DIR
CSV_PATH = BASE_DIR + CSV_DIR

@app.route('/', methods=['GET', 'POST'])
def index():
    img_name = ""
    ori_data=["",""]
    edit_data=["",""]
    N_cols=""
    isedit=""
    cols=["r","g","b"]
    data_img=[]
    if request.method == 'POST':
        img_file = request.files['image']
        N_cols = request.form['name']
        if img_file=="" or N_cols=="":
            pass
        else:
            N_cols=int(N_cols)
            filename = secure_filename(img_file.filename)
            img_url = os.path.join(app.config['UPLOAD_FOLDER'], "original.jpg")
            img_file.save(img_url)
            ori=Image.open(os.path.join(IMG_PATH + "original.jpg"))
            ori_ar=np.asarray(ori)
            print(ori_ar.shape)
            img_name="ok"

            print("img uploaded")



    if request.method == 'GET':
        print("get")
    return render_template('index.html', img_name=img_name,
        isedit=isedit, header_ori=ori_data[0], record_ori=ori_data[1],
        N=N_cols,header_edit=edit_data[0], record_edit=edit_data[1]
    )



if __name__ == '__main__':
    app.debug = True
    app.run()