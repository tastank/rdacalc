#!/usr/bin/python
import datetime
import os
import pygrib
import tempfile
from ftplib import FTP

DIR = tempfile.mkdtemp()
# This script may run over several minutes, so use one time rather than multiple utcnow() calls
HRRR_TIME = datetime.datetime.utcnow() - datetime.timedelta(hours=1)
HRRR_FTP = "ftp.ncep.noaa.gov"
HRRR_DIR = "/pub/data/nccf/com/hrrr/prod/hrrr.%Y%m%d/"
HRRR_FN = "hrrr.t%Hz.wrfprsf{:0>2}.grib2"

# Download HRRR file given forecast hour, issue time, and directory
def download_hrrr_prsf(fh, issue_time=HRRR_TIME, dir_=DIR):
    hrrr_dir = issue_time.strftime(HRRR_DIR)
    hrrr_fn = issue_time.strftime(HRRR_FN).format(fh)
    local_hrrr_fn = os.path.join(dir_, hrrr_fn)
    ftp = FTP(HRRR_FTP)
    ftp.login()
    ftp.cwd(hrrr_dir)
    ftp.retrbinary("RETR {}".format(hrrr_fn), open(local_hrrr_fn, 'wb').write)
    return local_hrrr_fn

# Sort grib entries by level
def level_key(g):
    return g.level

def get_temp_grib(grib):
    temp_grib = []
    for g in grib:
        if g.name == "Temperature" and g.typeOfLevel == "isobaricInhPa":
            temp_grib.append(g)
    grib.rewind()
    return sorted(temp_grib, key=level_key, reverse=True)

def get_hght_grib(grib):
    hght_grib = []
    for g in grib:
        if g.name == "Temperature" and g.typeOfLevel == "isobaricInhPa":
            hght_grib.append(g)
    grib.rewind()
    return sorted(hght_grib, key=level_key, reverse=True)

if __name__ == "__main__":

    # Downlaod HRRR files for forecast hours 0-3
    for fh in range(0, 3+1):
        local_hrrr_fn = download_hrrr_prsf(fh)
        # HRRR pressure field files are pretty large, so extract what is needed from each then remove it
        grib = pygrib.open(hrrr_fn)
        temp_grib = get_temp_grib(grib)
        hght_grib = get_hght_grib(grib)
        os.remove(local_hrrr_fn)
