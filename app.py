# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from werkzeug.utils import secure_filename
import os
from PIL import Image
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.cluster import MiniBatchKMeans
import io
import pickle
import time
app = Flask(__name__, static_url_path="")

UPLOAD_FOLDER = './static/images/'
UPLOAD_FOLDER2 ='./static/csv/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['UPLOAD_FOLDER2'] = UPLOAD_FOLDER2
app.config.from_object(__name__)

cols=["r","g","b"]

IMG_DIR = "/static/images/"
CSV_DIR = "/static/csv/"
BASE_DIR = os.path.dirname(__file__)
IMG_PATH = BASE_DIR + IMG_DIR
CSV_PATH = BASE_DIR + CSV_DIR


cols=["r","g","b"]
def decopri(txt):
    print("-" * 80)
    if len(str(txt)) < 80:
        print(" " * int((80 - len(str(txt))) / 2) + str(txt) + " " * int((80 - len(str(txt))) / 2))
    else:
        print(str(txt))
    print("-" * 80)
def rgb2hex(rgb):
    cop = rgb.copy()
    li = ["a", "b", "c", "d", "e", "f"]
    hex = "#"
    for i in range(3):
        if cop[i] / 16 >= 10:
            hex += li[int(cop[i] / 16) - 10]
            cop[i] %= 16
        else:
            hex += str(int(cop[i] / 16))
            cop[i] %= 16
        if cop[i] >= 10:
            hex += li[cop[i] - 10]
        else:
            hex += str(cop[i])
    return hex

def hex2rgb(h):
    li = ["a", "b", "c", "d", "e", "f"]
    h=h[1:]
    c=[0,0,0]
    for i in range(6):
        flag=0
        for j in range(6):
            if h[i]==li[j]:
                c[int(i/2)]+=(10+j)*(16**((i+1)%2))
                flag=1
        if flag==0:
            c[int(i/2)]+=int(h[i])*(16**((i+1)%2))
    return c[0],c[1],c[2]
  
def img2df(input_img):
    im_ar = input_img
    x, y, z = im_ar.shape[0], im_ar.shape[1], im_ar.shape[2]
    df = (pd.DataFrame(im_ar.reshape([x * y, z]))).rename(columns={0: "r", 1: "g", 2: "b"})
    # decopri("img２df completed successfully")
    return df, x, y, z


def color_grouping(df, N):
    # pred = KMeans(n_clusters=N).fit_predict(np.array(df))
    pred = MiniBatchKMeans(n_clusters=N).fit_predict(np.array(df))
    df["group"] = pred
    return df


def coltable(df, N):
    col_df = []
    for i in range(N):
        data_len = len(df[df["group"] == i])
        rgb = []
        for j in range(3):
            vc = df[df["group"] == i][cols[j]].value_counts()
            if np.array(vc.head(1))[0] / data_len >= 0.5:
                rgb.append(vc.keys()[0])
            else:
                rgb.append(int(df[df["group"] == i][cols[j]].mean()))
        #         col_df.append(rgb2hex(rgb))
        col_df.append(rgb)
    # decopri("coltable completed successfully")
    col_df = pd.DataFrame(col_df)
    return col_df


def rgbdf2hexdf(rgb_df):
    hexli = []
    for i in range(len(rgb_df)):
        hexli.append(rgb2hex(rgb_df.loc[i]))
    # decopri("rgb2hex completed successfully")
    return pd.DataFrame(hexli)


def rgbvalue(li, df):
    rgbv = []
    for i in range(len(li)):
        rgbvalue = "("
        for j in range(3):
            rgbvalue += str(li[i][j])
            if j != 2:
                rgbvalue += ","
        rgbvalue += ")"
        rgbvalue += "  " * 3 + df.loc[i]
        rgbv.append(rgbvalue)
    return rgbv


@app.route('/', methods=['POST','GET'])
def index():
    img_name = ""
    error_flag=""
    ori_data=["",""]
    edit_data=["",""]
    N_cols=""
    isedit=""
    cols=["r","g","b"]
    data_img=[]
    if request.method == 'POST':
        
        decopri("計測開始")
        start = time.time()
        
        img_file = request.files['image']
        N_cols = request.form['name']
        filename = secure_filename(img_file.filename)
        decopri("処理スタート")
        N_cols=int(N_cols)
        #構成色数が0以下の時エラー処理
        if N_cols<=0:
            error_flag="True"
            return render_template('index.html', img_name=img_name,error_case=error_flag)
        img_url = os.path.join(app.config['UPLOAD_FOLDER'], "original.jpg")
        img_file.save(img_url)
        ori=Image.open(os.path.join(app.config['UPLOAD_FOLDER'],"original.jpg"))
        decopri("step1 画像を保存終了:"+str(time.time() - start))
        if ori.width>ori.height:
            ori=ori.resize((200,int(ori.height*200/ori.width)),Image.LANCZOS)    
        else:
            ori=ori.resize((int(ori.width*200/ori.height),200),Image.LANCZOS)
        
        ori_ar=np.asarray(ori)[:,:,:3]
        img_name="ok"
        img_df,x,y,z=img2df(ori_ar)
        data_img.append(N_cols),data_img.append(x),data_img.append(y),data_img.append(z)
        img_df=color_grouping(img_df,N_cols)

        decopri("step2 グループ分け終了:"+str(time.time() - start))
        col_df=coltable(img_df,N_cols)
        # img_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'],"img.csv"),index=False)
        with open(os.path.join(app.config['UPLOAD_FOLDER'],"img.pickle"),'wb') as f:
            pickle.dump(img_df,f)
        decopri("step3 画像書き込み終了:"+str(time.time() - start))
        hex_ori_df=rgbdf2hexdf(col_df).rename(columns={0:"color code"})
        ori_data[0]= hex_ori_df.columns 
        ori_data[1] = hex_ori_df.values.tolist() 
        edit_data[0]=ori_data[0]
        edit_data[1]=ori_data[1]
        img_name = "ok"
        data_df=pd.DataFrame(data_img)
        data_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'] ,"data.csv"),index=False)
        hex_ori_df.to_csv(os.path.join(app.config['UPLOAD_FOLDER'] ,"original.csv"),index=False)
        decopri("step4 post終了:"+str(time.time() - start))
    return render_template('index.html', img_name=img_name,
        isedit=isedit, header_ori=ori_data[0], record_ori=ori_data[1],
        N=N_cols,header_edit=edit_data[0], record_edit=edit_data[1],error_case=error_flag
    )

@app.route('/editer', methods=['GET'])
def editer():
    img_name = ""
    error_flag=""
    ori_data=["",""]
    edit_data=["",""]
    N_cols=""
    isedit=""
    cols=["r","g","b"]
    data_img=[]
    if request.method == 'GET':
        if os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'] ,"data.csv")):
            img_name = "ok"
            start = time.time()

            s=str(request.args.getlist('color'))
            s=s[1:-1]
            s=s.split(', ')
            for i in range(len(s)):
                s[i]=s[i][1:-1]
            col_li=s
            data_df=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'],"data.csv"))
            hex_edit_df=pd.DataFrame(col_li).rename(columns={0:"color"})
            hex_ori_df=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'] ,"original.csv"))
            # edit_df=pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'],"img.csv"))
            with open(os.path.join(app.config['UPLOAD_FOLDER'],"img.pickle"),'rb') as f:
                edit_df=pickle.load(f)


            for i in range(len(col_li)):
                r,g,b=hex2rgb(col_li[i])
                edit_df.loc[edit_df["group"]==i,"r"]=r
                edit_df.loc[edit_df["group"]==i,"g"]=g
                edit_df.loc[edit_df["group"]==i,"b"]=b
            edit_df=edit_df.drop("group",axis=1)
            ori_data[0] = hex_ori_df.columns 
            ori_data[1] = hex_ori_df.values.tolist()
            edit_data[0] = hex_edit_df.columns 
            edit_data[1] = hex_edit_df.values.tolist()
            N_cols=int(data_df.loc[0])
            x=int(data_df.loc[1])
            y=int(data_df.loc[2])
            edit_img=np.array(edit_df)
            edit_ar=edit_img.reshape([x,y,3])
            print(edit_ar.shape)
            edit_img = Image.fromarray(np.uint8(edit_ar))
            isedit=True
            edit_img.save(os.path.join(app.config['UPLOAD_FOLDER'],"edit.jpg"))
            decopri("処理終了:"+str(time.time() - start))

    return render_template('index.html', img_name=img_name,
        isedit=isedit, header_ori=ori_data[0], record_ori=ori_data[1],
        N=N_cols,header_edit=edit_data[0], record_edit=edit_data[1],error_case=error_flag
    )
if __name__ == '__main__':
    app.debug = True
    app.run(host='0.0.0.0')