from db_util.activity_save import ActivitySave
from parsers.fit.fit_handler import FitHandler


def run_main():
    fit_path = '/Volumes/ctbackup/garmin_files/B49C3819.FIT'
    db = ActivitySave()
    fh = FitHandler(fit_path, db)
    fh.handle_file()
    db.close()


if __name__ == '__main__':
    run_main()
