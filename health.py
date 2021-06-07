import os

from flask import (
    Blueprint, current_app, flash, redirect, render_template, request, url_for, session
)
from werkzeug.utils import secure_filename
from auth import login_required
from db import get_db
from db_util.activity_models import ActivityData
from db_util.activity_save import ActivitySave
from db_util.file_hash import FileHash
from db_util.query_adapters import query_activity_list, query_activity_detail, update_user_info, query_user_info, \
    miles_to_km, query_activity_summary
from parsers.fit.fit_handler import FitHandler

ALLOWED_EXTENSIONS = {'fit'}

bp = Blueprint('health', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@bp.route('/')
@login_required
def index():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            db_conn = get_db()
            dat = query_activity_list(db_conn, user_id)
            return render_template('health/index.html', data=dat)
    return render_template('health/index.html')


@bp.route('/activity_detail.html', methods=('GET', 'DELETE'))
@login_required
def activity_detail():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            activity_id = request.args.get('actid')
            db_conn = get_db()
            dat = query_activity_detail(db_conn, user_id, activity_id)
            return render_template('health/activity_detail.html', data=dat)
    if request.method == 'DELETE':
        if 'user_id' in session:
            user_id = session['user_id']
            activity_id = request.args.get('actid')
            db_conn = get_db()
            db = ActivitySave(db_conn, '', user_id)
            act = ActivityData()
            act.id = activity_id
            act.user_id = user_id
            db.delete_activity(act)
            flash('Activity deleted')
            return redirect(url_for('index'), code=303)

    return render_template('health/activity_detail.html')


@bp.route('/activity_summary.html')
@login_required
def activity_summary():
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            activity_id = request.args.get('actid')
            db_conn = get_db()
            dat = query_activity_summary(db_conn, activity_id)
            return render_template('health/activity_summary.html', data=dat)
    return render_template('health/activity_summary.html')


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
            # TODO: Improve handling - maybe as a background process
            user_id = session.get('user_id')
            if user_id is not None:
                hash_str = FileHash.hash_file(saved_filepath)
                db_conn = get_db()
                db = ActivitySave(db_conn, hash_str, user_id)
                if not db.is_previously_uploaded():
                    fh = FitHandler(saved_filepath, db)
                    fh.handle_file()
                    flash('File uploaded!')
                    return redirect(url_for('index'))
                else:
                    flash('File previously uploaded!')

    return render_template('health/upload.html')


@bp.route('/user_info', methods=('GET', 'POST'))
@login_required
def user_info():
    db = get_db()
    if 'user_id' in session:
        user_id = session['user_id']
        if request.method == 'POST':
            birthdate = request.form['birthdate']
            target_distance = request.form['target_distance']
            target_time = request.form['target_time']
            km = miles_to_km(float(target_distance))
            update_user_info(db, user_id, birthdate, km, target_time)
            flash('User information updated')
            return redirect(url_for('index'))
        else:
            dat = query_user_info(db, user_id)
            return render_template('health/user_info.html', user_info=dat)
