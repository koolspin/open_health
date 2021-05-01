import os
import datetime

from flask import (
    Blueprint, current_app, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from auth import login_required
from db import get_db
from db_util.activity_load import ActivityLoad
from db_util.activity_save import ActivitySave
from db_util.file_hash import FileHash
from parsers.fit.fit_handler import FitHandler

ALLOWED_EXTENSIONS = {'fit'}

bp = Blueprint('health', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_distance(km):
    km_to_miles_conversion = 0.621371
    miles = km * km_to_miles_conversion
    return miles


def convert_temp(cel):
    fa = (cel * 1.8) + 32.0
    return fa


@bp.route('/')
@login_required
def index():
    activity_sel = 'select id, activity_date as "ad [timestamp]", activity_type, activity_sub_type from activity where user_id = ? order by activity_date'
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            db_conn = get_db()
            cur = db_conn.cursor()
            cur.execute(activity_sel, (user_id,))
            data = []
            for row in cur:
                col = []
                col.append(row[0])
                col.append(row[1])
                col.append(row[2])
                col.append(row[3])
                act_load = ActivityLoad(db_conn)
                act_sum = act_load.load_activity_sum(row[0])
                total_dist = act_sum.kvps.get("total_distance")
                if total_dist is not None:
                    col.append(convert_distance(total_dist / 1000.0))
                else:
                    col.append(None)
                total_time = act_sum.kvps.get("total_timer_time")
                if total_dist is not None:
                    elapsed_time = datetime.timedelta(seconds=int(total_time))
                    col.append(str(elapsed_time))
                else:
                    col.append(None)
                data.append(col)
            cur.close()
            return render_template('health/index.html', data=data)
    return render_template('health/index.html')


@bp.route('/activity_detail.html')
@login_required
def activity_detail():
    activity_detail = 'select r.timestamp as "ad [timestamp]", r.lat, r.long, r.heart_rate, r.distance, r.altitude, r.speed, ' \
                      'r.temperature from activity_record r inner join activity a on r.activity_id = a.id ' \
                      'where a.user_id = ? and r.activity_id = ? order by r.timestamp'
    if request.method == 'GET':
        if 'user_id' in session:
            user_id = session['user_id']
            activity_id = request.args.get('actid')
            db_conn = get_db()
            cur = db_conn.cursor()
            cur.execute(activity_detail, (user_id, activity_id))
            data = []
            for row in cur:
                # Convert to km, the possibly to miles?
                col = []
                col.append(row[0])
                col.append(row[1])
                col.append(row[2])
                col.append(row[3])
                if row[4] is not None:
                    col.append(convert_distance(row[4] / 1000.0))
                else:
                    col.append(None)
                if row[5] is not None:
                    col.append(convert_distance(row[5] / 1000.0))
                else:
                    col.append(None)
                if row[6] is not None:
                    col.append(convert_distance(row[6] / 1000.0) * 3600.0)
                else:
                    col.append(None)
                if row[7] is not None:
                    col.append(convert_temp(row[7]))
                else:
                    col.append(None)
                data.append(col)
            cur.close()
            return render_template('health/activity_detail.html', data=data)
    return render_template('health/activity_detail.html')


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