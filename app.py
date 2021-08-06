# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory

app = Flask(__name__)




@app.route('/', methods=['GET', 'POST'])
def index():
    img_name = ""
    if request.method == 'POST':
        stream = request.files['image'].stream
        N_cols = request.form['name']
        print("img uploaded")
    if request.method == 'GET':
        print("get")
    return render_template('index.html', img_name=img_name)



if __name__ == '__main__':
    app.debug = True
    app.run()