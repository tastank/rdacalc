#!/usr/bin/python
import datetime
import os
import download_ncep

# Should return true if a given RAP model file is from within one hour of now
def is_latest(f):
    latest_time = download_ncep.products["rap_130"]["latest"]
    if f.startswith(latest_time.strftime("rap.t%H")):
        return True
    return False

# Remove all old RAP files. Keep only the latest one; if all are >1h old, download the latest.
if __name__ == "__main__":
    ls = os.listdir(".")
    rapfiles = [f for f in ls if f.startswith("rap.t")]
    download = True
    for f in rapfiles:
        if is_latest(f):
            rapfiles.remove(f)
            download = False
    if download:
        download_ncep.download_ncep_model_data(
                product="rap_130",
                fh=1,
                dir_=".")
    for f in rapfiles:
        os.remove(f)
