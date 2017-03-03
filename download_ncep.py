#!/usr/bin/python
import argparse
import datetime
import os
import tempfile
from ftplib import FTP

# download_hrrr_prsf() may be called several times over several minutes, so use one time rather than multiple utcnow() calls
NCEP_FTP = "ftp.ncep.noaa.gov"ksdflkjasdflkjasdflkjsdfalkj

HRRR_TIME = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
HRRR_DIR = "/pub/data/nccf/com/hrrr/prod/hrrr.%Y%m%d/"
HRRR_PRSF_FN = "hrrr.t%Hz.wrfprsf{:0>2}.grib2"

RAP_TIME = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
RAP_DIR = "/pub/data/nccf/com/rap/prod/rap.%Y%m%d/"
RAP_AWIP_FN = "rap.t%Hz.awp130pgrbf{:0>2}.grib2"

products = {
    "hrrr_prsf": {
        "latest": HRRR_TIME,
        "ftp_dir": HRRR_DIR,
        "fn": HRRR_PRSF_FN,
        "available": "Yesterday through one hour ago",
        "full_name": "HRRR Pressure Fields, 3km CONUS"
    },
    "rap_218": {
        "latest": RAP_TIME,
        "ftp_dir": RAP_DIR,
        "fn": RAP_AWIP_FN,
        "available": "Yesterday through one hour ago",
        "full_name": "RAP Pressure Fields, 13km CONUS"
    }
}

# Download HRRR file given forecast hour, issue time, and directory
def download_ncep_model_data(product="hrrr_prsf", fh=1, issue_time=None, dir_='.'):
    product = products[product]
    if issue_time is None:
        issue_time = product["latest"]
    ftp_dir = issue_time.strftime(product["ftp_dir"])
    ftp_fn = issue_time.strftime(product["fn"]).format(fh)
    local_fn = os.path.join(dir_, ftp_fn)
    ftp = FTP(NCEP_FTP)
    ftp.login()
    ftp.cwd(ftp_dir)
    ftp.retrbinary("RETR {}".format(ftp_fn), open(local_fn, 'wb').write)
    return local_fn

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download NCEP model data. All times are UTC.")
    parser.add_argument("--dir", "-d", default='.', help="Directory to save files, default ./")
    parser.add_argument("--product", "-p", default="hrrr_prsf", help="Product to download. One of {hrrr_prsf, rap_218}")
    parser.add_argument("--date", default=HRRR_TIME.strftime("%Y%m%d"), help="YYYYMMDD UTC date of model to download. Availability depends on product.")
    parser.add_argument("--hour", type=int, default=HRRR_TIME.hour, help="UTC model run hour to download, default one hour ago")
    parser.add_argument("--fh", type=int, default=1, help="Forecast hour to download, default 1")

    args = parser.parse_args()
    download_ncep_model_data(
            args.product,
            args.fh,
            datetime.datetime.strptime("{}{:0>2}".format(args.date, args.hour), "%Y%m%d%H"),
            args.dir)

