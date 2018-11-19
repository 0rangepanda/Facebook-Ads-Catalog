#!flask/bin/python

import os
import PIL
from PIL import Image
import simplejson
import traceback

from flask import Flask, request, render_template, redirect, url_for, send_from_directory
from flask_bootstrap import Bootstrap
from werkzeug import secure_filename

from lib.upload_file import uploadfile
from lib.facebookads.crmlsziphandler import CrmlsZipHandler


app = Flask(__name__)
app.config['DEBUT'] = True
app.config['SECRET_KEY'] = 'hard to guess string'
# use abspath
app.config['FB_CONFIG'] = '/home/flask/app/backend/config/fbcsv.ini'
app.config['UPLOAD_FOLDER'] = '/home/flask/app/backend/data/'
app.config['TMP_UPLOAD_FOLDER'] = '/home/flask/app/backend/data/tmp'
app.config['THUMBNAIL_FOLDER'] = '/home/flask/app/backend/data/thumbnail/'
app.config['RESULTS_FOLDER'] = '/home/flask/app/backend/data/results/'
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

#ALLOWED_EXTENSIONS = set(['txt', 'gif', 'png', 'jpg', 'jpeg', 'bmp', 'rar', 'zip', '7zip', 'doc', 'docx'])
ALLOWED_EXTENSIONS = set(['zip'])
IGNORED_FILES = set(['.gitignore'])

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


def create_thumbnail(image):
    try:
        base_width = 80
        img = Image.open(os.path.join(app.config['UPLOAD_FOLDER'], image))
        w_percent = (base_width / float(img.size[0]))
        h_size = int((float(img.size[1]) * float(w_percent)))
        img = img.resize((base_width, h_size), PIL.Image.ANTIALIAS)
        img.save(os.path.join(app.config['THUMBNAIL_FOLDER'], image))

        return True

    except:
        print(traceback.format_exc())
        return False


@app.route("/upload", methods=['GET', 'POST'])
def upload():
    if request.method == 'POST':
        files = request.files['file']

        if files:
            filename = secure_filename(files.filename)
            filename = gen_file_name(filename)
            mime_type = files.content_type

            if not allowed_file(files.filename):
                result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File type not allowed")

            else:
                # save file to disk
                uploaded_file_path = os.path.join(app.config['TMP_UPLOAD_FOLDER'], filename)
                files.save(uploaded_file_path)

                # Process after saving
                try:
                    crmlszip = CrmlsZipHandler(
                        uploaded_file_path, app.config['FB_CONFIG'],
                        app.config['UPLOAD_FOLDER'], app.config['UPLOAD_FOLDER']
                    )
                    crmlszip.unzip()
                    xmlfile_path = crmlszip.handle()
                except:
                    result = uploadfile(name=filename, type=mime_type, size=0, not_allowed_msg="File process failed")
                    return simplejson.dumps({"files": [result.get_file()]})

                # create thumbnail after saving (for image)
                if mime_type.startswith('image'):
                    create_thumbnail(filename)

                # get file size after saving
                #size = os.path.getsize(uploaded_file_path)
                size = os.path.getsize(xmlfile_path)
                xmlfile_name = os.path.basename(xmlfile_path)

                # return json for js call back
                #result = uploadfile(name=filename, type=mime_type, size=size)
                result = uploadfile(name=xmlfile_name, type=mime_type, size=size)

            return simplejson.dumps({"files": [result.get_file()]})

    if request.method == 'GET':
        # get all file in ./data directory
        files = [f for f in os.listdir(app.config['UPLOAD_FOLDER']) if
                 os.path.isfile(os.path.join(app.config['UPLOAD_FOLDER'], f)) and f not in IGNORED_FILES]

        file_display = []

        for f in files:
            size = os.path.getsize(os.path.join(app.config['UPLOAD_FOLDER'], f))
            file_saved = uploadfile(name=f, size=size)
            file_display.append(file_saved.get_file())

        return simplejson.dumps({"files": file_display})

    return redirect(url_for('index'))


@app.route("/delete/<string:filename>", methods=['DELETE'])
def delete(filename):
    """
    On delete ...
    :param filename:
    :return:
    """
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file_thumb_path = os.path.join(app.config['THUMBNAIL_FOLDER'], filename)

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
            if os.path.exists(file_thumb_path):
                os.remove(file_thumb_path)

            return simplejson.dumps({filename: 'True'})
        except:
            return simplejson.dumps({filename: 'False'})


# serve static files
@app.route("/thumbnail/<string:filename>", methods=['GET'])
def get_thumbnail(filename):
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename=filename)


@app.route("/data/<string:filename>", methods=['GET'])
def get_file(filename):
    return send_from_directory(os.path.join(app.config['UPLOAD_FOLDER']), filename=filename)


@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')