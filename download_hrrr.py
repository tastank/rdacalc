#!/usr/bin/python
import argparse
import datetime
import os
import tempfile
from ftplib import FTP

# download_hrrr_prsf() may be called several times over several minutes, so use one time rather than multiple utcnow() calls
HRRR_TIME = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
HRRR_FTP = "ftp.ncep.noaa.gov"
HRRR_DIR = "/pub/data/nccf/com/hrrr/prod/hrrr.%Y%m%d/"
HRRR_FN = "hrrr.t%Hz.wrfprsf{:0>2}.grib2"

# Download HRRR file given forecast hour, issue time, and directory
def download_hrrr_prsf(fh, issue_time=HRRR_TIME, dir_='.'):
    hrrr_dir = issue_time.strftime(HRRR_DIR)
    hrrr_fn = issue_time.strftime(HRRR_FN).format(fh)
    local_hrrr_fn = os.path.join(dir_, hrrr_fn)
    ftp = FTP(HRRR_FTP)
    ftp.login()
    ftp.cwd(hrrr_dir)
    ftp.retrbinary("RETR {}".format(hrrr_fn), open(local_hrrr_fn, 'wb').write)
    return local_hrrr_fn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download HRRR data.")
    parser.add_argument("--dir", "-d", default='.', help="Directory to save HRRR file")
    parser.add_argument("--date", default=HRRR_TIME.strftime("%Y%m%d"), help="YYYYMMDD UTC date of HRRR model to download. Only today and yesterday will be available.")
    parser.add_argument("--hour", "-h", type=int, default=HRRR_TIME.hour, help="UTC model run hour to download (default one hour ago)")
    parser.add_argument("--fh", type=int, default=1, help="Forecast hour to download (0-18), default 1")

    args = parser.parse_args()
    download_hrrr_prsf(
            args.fh,
            datetime.datetime.strptime("{}{:0>2}".format(args.date, args.hour), "%Y%m%d%H"),
            args.dir)

