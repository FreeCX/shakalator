from flask import Flask, render_template, redirect, url_for
from flask import request, jsonify, send_file
from multiprocessing import Process, Pipe
from werkzeug import secure_filename
from os import path, system, remove
from hashlib import md5
import time


# 5m
TIME_DELTA = 5 * 60


""" инициализируем flask """
app = Flask(__name__, static_url_path='')
""" настраиваем папку для загрузки файлов """
app.config['UPLOAD_FOLDER'] = path.join(path.dirname(path.realpath(__file__)), 'upload')


def get_hash(text):
    return md5(text.encode('utf-8')).hexdigest()


# главный поток обработки
def handler(conn):
    clean_list = []
    while True:
        if conn.poll(10):
            data = conn.recv()
            sh_thread = Process(target=gs_shakalizing, args=data)
            sh_thread.start()
            sh_thread.join()
            clean_list.append((data[1], time.clock_gettime(0)))
        curr_time = time.clock_gettime(0)
        new_list = []
        for (filename, l_time) in clean_list:
            delta = curr_time - l_time
            if delta > TIME_DELTA:
                gen_file = path.join(app.config['UPLOAD_FOLDER'], filename)
                remove(gen_file)
            else:
                new_list.append((filename, l_time))
        clean_list = new_list


# обрабатываем файл
def gs_shakalizing(filename, new_name, dpi):
    old_file = path.join(app.config['UPLOAD_FOLDER'], filename)
    new_file = path.join(app.config['UPLOAD_FOLDER'], new_name)
    cmd = """/usr/bin/gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.5 -dPDFSETTINGS=/ebook -dNOPAUSE \
             -dQUIET -dBATCH -dColorImageResolution={dpi} -sOutputFile='{output}' '{input}'\
          """.format(dpi=dpi, output=new_file, input=old_file)
    system(cmd)
    remove(old_file)


# проверяем статус обработки
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


# загрузка файла и страница с ожиданием
@app.route('/shakalazing', methods=['POST', 'GET'])
def shakalazing():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            file.save(path.join(app.config['UPLOAD_FOLDER'], filename))
            dpi = request.form.get('dpi')
            hash_code = get_hash(filename + time.strftime('%H:%M:%S'))
            parent_conn.send((filename, hash_code, dpi))
            return redirect(url_for('shakalazing', code=hash_code))
        else:
            return redirect(url_for('index'))
    else:
        return render_template('shakalazing.html', code=request.values.get('code'))


# главная страница
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    main_proc = Process(target=handler, args=(child_conn,))
    main_proc.start()
    app.run(host='0.0.0.0', port='5000')
    main_proc.join()
