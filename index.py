from flask import *
import os
from werkzeug import secure_filename
from embroidery_maker import *
from database import load_data_from_db
import options

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['ALLOWED_EXTENSIONS'] = set(['png', 'jpg', 'jpeg'])

basedir = os.path.abspath(os.path.dirname(__file__))
updir = os.path.join(basedir, 'upload/')

DATA = database.load_data_from_db(options.DB_PATH)
MAKER = EmbroideryMaker(DATA[0], DATA[1])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    url_style = url_for('static', filename='style.css')
    url_validation_script = url_for('static', filename='validation.js')

    return render_template('index.html', style=url_style, validation_script=url_validation_script)

@app.route('/gen_embroidery', methods=['POST'])
def generate_embroidery():
    if request.method == 'POST':
        app.logger.debug("is json:" + str(request.is_json) )
        app.logger.debug("json: " + str(request.json))
        content = request.get_json(silent=True)
        e_size = (int(float(request.json['e_width'])) , int(float(request.json['e_height'])))
        o_size = (int(float(request.json['o_width'])) , int(float(request.json['o_height'])))
        xy_num = 0 if request.json['xy_num'] == '' else int(request.json['xy_num'])
        xy = (True if request.json['xy_bool'] == '1' else False, xy_num, xy_num)
        colors = int(request.json['colors'])
        path = os.path.join(updir, str(request.json['img_name']))
        img = MAKER.gen_embroidery(cv2.imread(path, cv2.IMREAD_COLOR ), e_size, o_size, xy, colors)
        embroider_path = os.path.join(options.EMBROIDERIES_FOLDER, str(request.json['img_name']));
        cv2.imwrite(embroider_path, img)

        return jsonify(url=url_for('static', filename=str(request.json['img_name'])))


@app.route('/upload_image', methods=['POST'])
def upload_image():
    if request.method == 'POST':
        files = request.files['file']
        if files and allowed_file(files.filename):
            filename = secure_filename(files.filename)
            app.logger.info('FileName: ' + filename)
            files.save(os.path.join(updir, filename))
            file_size = os.path.getsize(os.path.join(updir, filename))
            app.logger.info('path: ' + os.path.join(updir, filename))
            size = get_img_size(os.path.join(updir, filename))
            return jsonify(width=size[0], height=size[1], name=filename, size=file_size)
