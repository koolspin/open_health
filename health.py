import math
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
from db_util.activity_models import ActivityData
from db_util.activity_save import ActivitySave
from db_util.file_hash import FileHash
from parsers.fit.fit_handler import FitHandler

ALLOWED_EXTENSIONS = {'fit'}

bp = Blueprint('health', __name__)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def miles_to_km(miles):
    miles_to_km_conversion = 1.60934
    km = miles * miles_to_km_conversion
    return km


def km_to_miles(km):
    km_to_miles_conversion = 0.621371
    miles = km * km_to_miles_conversion
    return miles


def convert_height(meters):
    meters_to_feet_conversion = 3.28084
    feet = meters * meters_to_feet_conversion
    return feet


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
                act_id = row[0]
                act_load = ActivityLoad(db_conn)
                total_dist = act_load.get_summed_column(act_id, "total_distance")
                if total_dist is not None:
                    col.append(km_to_miles(total_dist / 1000.0))
                else:
                    col.append(None)
                total_time = act_load.get_summed_column(act_id, "total_timer_time")
                if total_time is not None:
                    elapsed_time = datetime.timedelta(seconds=int(total_time))
                    col.append(str(elapsed_time))
                else:
                    col.append(None)
                data.append(col)
            cur.close()
            return render_template('health/index.html', data=data)
    return render_template('health/index.html')


@bp.route('/activity_detail.html', methods=('GET', 'DELETE'))
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
            act_load = ActivityLoad(db_conn)
            all_laps = act_load.load_lap_sum(activity_id)
            if len(all_laps) > 0:
                cur_lap_start = next(iter(all_laps))
            else:
                cur_lap_start = None
            cur = db_conn.cursor()
            cur.execute(activity_detail, (user_id, activity_id))
            data = []
            for row in cur:
                # Convert to km, the possibly to miles?
                col = []
                cur_start_time = row[0]
                col.append(row[0])
                col.append(row[1])
                col.append(row[2])
                col.append(row[3])
                if row[4] is not None:
                    col.append(km_to_miles(row[4] / 1000.0))
                else:
                    col.append(None)
                if row[5] is not None:
                    # It looks like the alititude records are already scaled and offset by the fitdecode lib
                    # So here we just convert to the preferred height scale
                    col.append(convert_height(row[5]))
                else:
                    col.append(None)
                if row[6] is not None:
                    col.append(km_to_miles(row[6] / 1000.0) * 3600.0)
                else:
                    col.append(None)
                if row[7] is not None:
                    col.append(convert_temp(row[7]))
                else:
                    col.append(None)
                if cur_lap_start is not None and cur_start_time >= cur_lap_start:
                    lap = all_laps.get(cur_lap_start)
                    lap_num = lap.session_num + 1
                    all_laps.pop(cur_lap_start, None)
                    col.append(lap_num)
                    if len(all_laps) > 0:
                        cur_lap_start = next(iter(all_laps))
                    else:
                        cur_lap_start = None
                else:
                    col.append(None)
                data.append(col)
            cur.close()
            return render_template('health/activity_detail.html', data=data)
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
            db.execute(
                "update user set birth_date = ?, target_weekly_distance = ?, target_weekly_time = ? where id = ?",
                (birthdate, km, target_time, user_id)
            )
            db.commit()
            flash('User information updated')
            return redirect(url_for('index'))
        else:
            user_info = db.execute(
                'SELECT birth_date, target_weekly_distance, target_weekly_time FROM user WHERE id = ?', (user_id,)
            ).fetchone()
            user_data = []
            age = None
            for ix in range(len(user_info)):
                if ix == 0:
                    if user_info[ix] is not None:
                        td = datetime.timedelta(days=365.25)
                        # age = datetime.date.today().year - user_info[ix].year
                        age = datetime.date.today() - user_info[ix]
                        age = math.trunc(age / td)
                if ix == 1:
                    if user_info[ix] is not None:
                        user_data.append(round(km_to_miles(user_info[ix]), 1))
                    else:
                        user_data.append(0)
                else:
                    user_data.append(user_info[ix])
            user_data.append(age)
            return render_template('health/user_info.html', user_info=user_data)

