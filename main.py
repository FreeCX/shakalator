from flask import Flask, render_template, redirect, url_for
from flask import request, jsonify, send_file
from werkzeug import secure_filename
from os import path, system, remove
from multiprocessing import Process
from hashlib import md5
import time

""" инициализируем flask """
app = Flask(__name__, static_url_path='')
""" настраиваем папку для загрузки файлов """
app.config['UPLOAD_FOLDER'] = path.join(path.dirname(path.realpath(__file__)), 'upload')

def get_hash(text):
    return md5(text.encode('utf-8')).hexdigest()

""" обрабатываем файл """
def gs_shakalizing(filename, new_name, dpi):
    old_file = path.join(app.config['UPLOAD_FOLDER'], filename)
    new_file = path.join(app.config['UPLOAD_FOLDER'], new_name)
    cmd = """/usr/bin/gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/ebook -dNOPAUSE \
             -dQUIET -dBATCH -dColorImageResolution={dpi} -sOutputFile='{output}' '{input}'\
          """.format(dpi=dpi, output=new_file, input=old_file)
    system(cmd)
    remove(old_file)

""" проверяем статус обработки """
@app.route('/process', methods=['POST', 'GET'])
def process():
    if request.method == 'POST':
        if request.json:
            filename = request.json.get('code')
            file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            if path.isfile(file_path):
                return jsonify({"status": "founded"})
            else:
                return jsonify({"status": "not found"})
        else:
            return jsonify({"status": "error"})
    else:
        filename = request.values.get('code')
        if filename:
            file_path = path.join(app.config['UPLOAD_FOLDER'], filename)
            return send_file(file_path, mimetype='application/pdf', 
                as_attachment=True, attachment_filename=filename + '.pdf')
        else:
            return 404

""" загрузка файла и страница с ожиданием """
@app.route('/shakalazing', methods=['POST', 'GET'])
def shakalazing():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
            dpi = request.form.get('dpi')
            hash_code = get_hash(filename)
            sh_thread = Process(target=gs_shakalizing, args=(filename, hash_code, dpi))
            sh_thread.start()
            return redirect(url_for('shakalazing', code=hash_code))
        else:
            return redirect(url_for('index'))
    else:
        return render_template('shakalazing.html', code=request.values.get('code'))

""" главная страница """
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run()