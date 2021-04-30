import os
from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from auth import login_required
from db import get_db
from db_util.activity_save import ActivitySave
from parsers.fit.fit_handler import FitHandler

ALLOWED_EXTENSIONS = {'fit'}

bp = Blueprint('health', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def index():
    activity_sel = 'select activity_date as "ad [timestamp]", activity_type, activity_sub_type from activity where user_id = ? order by activity_date'
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            db_conn = get_db()
            cur = db_conn.cursor()
            cur.execute(activity_sel, (user_id,))
            data = cur.fetchall()
            cur.close()
            return render_template('health/index.html', data=data)
    return render_template('health/index.html')


@bp.route('/upload', methods=('GET', 'POST'))
@login_required
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'datafile' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['datafile']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            saved_filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            file.save(saved_filepath)
            flash('File uploaded!')
            # TODO: Improve handling - maybe as a background process
            db_conn = get_db()
            db = ActivitySave(db_conn)
            fh = FitHandler(saved_filepath, db)
            fh.handle_file()
            #
            return redirect(url_for('index'))

    return render_template('health/upload.html')