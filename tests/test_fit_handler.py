import sqlite3
from db_util.activity_save import ActivitySave
from parsers.fit.fit_handler import FitHandler


def run_main():
    fit_path = '/Volumes/ctbackup/garmin_files/B49C3819.FIT'
    db_conn = sqlite3.connect('/Users/cturner/Documents/personal/projects/open_health/docs/open_health.sqlite')
    db = ActivitySave(db_conn)
    fh = FitHandler(fit_path, db)
    fh.handle_file()
    db_conn.close()


if __name__ == '__main__':
    run_main()
