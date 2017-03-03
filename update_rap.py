#!/usr/bin/python
import argparse
import datetime
import os
import download_ncep

#Run this at the top of every hour with cron

# Should return true if a given RAP model file is from within one hour of now
def is_latest(f):
    latest_time = download_ncep.products["rap_130"]["latest"]
    if f.startswith(latest_time.strftime("rap.t%H")):
        return True
    return False

# Remove all old RAP files. Keep only the latest one; if all are >1h old, download the latest.
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update RAP file in this directory if a newer file exists")
    parser.add_argument("--verbose", "-v", action="store_true", help="Print the name of the latest stored RAP file")
    args = parser.parse_args()

    ls = os.listdir(".")
    rapfiles = [f for f in ls if f.startswith("rap.t")]
    download = True
    for f in rapfiles:
        if is_latest(f):
            latest_fn = f
            rapfiles.remove(f)
            download = False
    if download:
        latest_fn = download_ncep.download_ncep_model_data(
                product="rap_130",
                fh=1,
                dir_=".")
    for f in rapfiles:
        os.remove(f)
    if args.verbose:
        print latest_fn
