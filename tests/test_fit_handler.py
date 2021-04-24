from parsers.fit.fit_handler import FitHandler


def run_main():
    fit_path = '/Volumes/ctbackup/garmin_files/B49C3819.FIT'
    fh = FitHandler(fit_path)
    fh.handle_file()


if __name__ == '__main__':
    run_main()
