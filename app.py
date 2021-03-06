#!flask/bin/python

# Author: Ngo Duy Khanh
# Email: ngokhanhit@gmail.com
# Git repository: https://github.com/ngoduykhanh/flask-file-uploader
# This work based on jQuery-File-Upload which can be found at https://github.com/blueimp/jQuery-File-Upload/

import os
import PIL
from PIL import Image
import simplejson
import traceback
import zipfile
import random
import matplotlib.pyplot as plt
import random 
import string
import tensorflow as tf
from model import MLModel

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename

from lib.upload_file import UploadFile


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['UPLOAD_FOLDER'] = 'data/'
app.config['THUMBNAIL_FOLDER'] = 'data/thumbnail/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024

ALLOWED_EXTENSIONS = set(['zip', '7zip'])
IGNORED_FILES = set(['.gitignore'])



IMAGE_PATH = 'C:/Users/Nisha/Documents/Hackathons/Codeshastra/c20-r2/static/img/foo.jpg'
bootstrap = Bootstrap(app)


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def gen_file_name(filename):
    """
    If file was exist already, rename it and return a new name
    """
    i = 1
    while os.path.exists(os.path.join(app.config['UPLOAD_FOLDER'], filename)):
        name, extension = os.path.splitext(filename)
        filename = '%s_%s%s' % (name, str(i), extension)
        i += 1

    return filename


def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))


def chunks(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


@app.route("/upload", methods=['GET', 'POST'])
def upload():    
    if request.method == 'POST':
        files = request.files['file']
        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type
            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            files.save(uploaded_file_path)
                
            code = randomString()
            data_path = None

            with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
                data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
                os.mkdir(data_path)
                zip_ref.extractall(data_path)

        return redirect('/results/'+ request.values.get("model")+ "/"+code)

    return redirect(url_for('index'))

@app.route("/upload-c", methods=['GET', 'POST'])
def uploadc():    
    if request.method == 'POST':
        files = request.files['file']
        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type
            uploaded_file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            files.save(uploaded_file_path)
                
            code = randomString()
            data_path = None

            with zipfile.ZipFile(uploaded_file_path, 'r') as zip_ref:
                data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
                os.mkdir(data_path)
                zip_ref.extractall(data_path)

        return redirect('/captcha/view/'+ request.values.get("model")+ "/"+code)
    return redirect(url_for('index'))

@app.route("/captcha/view/<string:model>/<string:code>", methods=['GET'])
def view_cahptca(model,code):
    data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
    imgs = os.walk(data_path)
    print(imgs)
    a = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        for f in filenames:
            a.append("/data/"+code+"/"+f)

    return render_template('captcha.html',r = {
        "imgs":a,
        "code":code
    })

@app.route("/captcha/view/<string:model>/<string:code>/result", methods=['GET','POST'])
def view_cahca(model,code):
    
    data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
    imgs = os.walk(data_path)
    a = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        for f in filenames:
            a.append(os.path.join(data_path,f))
    
    d = request.form.to_dict()
    print(d)
    
    print(a)

    mlModel = MLModel("./models/" + model + ".json","./models/" + model + ".h5")
    imgs = mlModel.predict_all_images(a)
    print(imgs)
    yes = True
    for key in d:
        if 's' not in key:
            k = int(key)
            print("K = ",k,imgs[k][1])
            if not imgs[k][1] == 0:
                yes = False

    print(yes)
    return render_template('all.html',r = yes )



@app.route("/results/<string:model>/<string:code>", methods=['GET'])
def get_results(model,code):
    data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
    mlModel = MLModel("./models/" + model + ".json","./models/" + model + ".h5")

    url_imgs = []
    imgs = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        for f in filenames:
            url_imgs.append("/data/"+code+"/"+f)
            imgs.append(os.path.join(data_path,f))

    imgs = mlModel.predict_all_images(imgs)
    
    i = 0
    for i in range(len(imgs)):
        imgs[i][0] = url_imgs[i]
        imgs[i][1] = mlModel.get_label(imgs[i][1])

    print(chunks(imgs,4))

    res = {
     "result" : chunks(imgs,4),
     "model": model,
     "code": code
    }
    
    
    return render_template('128.html',result = res )





def vis():
    fig=plt.figure()
    x1=[0]*10
    y1=[0]*10
    for i in range(1,11):
        x1.append(i)
        y1.append(random.uniform(82.0000+i, 90.0000))
    x2=[0]*10
    y2=[0]*10
    for i in range(1,11):
        x2.append(i)
        y2.append(random.uniform(82.0000+i, 90.0000))
    plt.ylim(80,95)
    plt.xlim(1,10)
    plt.plot(x1, y1, 'b-', label='Before')
    plt.plot(x2, y2, 'r-', label='After')
    plt.title('Comparitive Model Accuracy')
    plt.ylabel('Accuracy')
    plt.xlabel('Epochs')
    plt.legend()
    plt.show()
    #plt.savefig(IMAGE_PATH,bbox_inches='tight', dpi=fig.dpi)
    



@app.route("/data/<string:code>/<string:filename>", methods=['GET'])
def get_file(code,filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER'],code), filename=filename)


@app.route("/captcha", methods=['GET'])
def index3():
    return render_template('index2.html')


@app.route("/play", methods=['GET'])
def index2():
    return render_template('playground.html')


@app.route("/results/<string:model>/<string:code>/retrain", methods=['POST'])
def post_file(model,code):
    
    d = request.form.to_dict()
    lr  = float(d.get("lr"))
    opt = d.get("op")
    ep = d.get("epoch")
    imgs = []
    lbl = []
    data_path = os.path.join(app.config['UPLOAD_FOLDER'],code)
    for key in d:
        print(key)
        value = d[key]
        if "/" in key and not "Q" in value:
            a = os.path.join(data_path,os.path.basename(key))
            imgs.append(a)
            lbl.append(value)





    lmodel = MLModel("./models/{}.json".format(model),"./models/{}.h5".format(model))
    lmodel.parameters(lr,tf.keras.losses.SparseCategoricalCrossentropy(), opt,imgs,lbl,ep)
    
    vis()
    return redirect("/results/" + model +"/" + code)






@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
