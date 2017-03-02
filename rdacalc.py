#!/usr/bin/python
import argparse
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

# ISA constants, found at https://wahiduddin.net/calc/density_altitude.htm
P0 = 101325 # MSL pressure, in Pa
T0 = 288.15 # MSL temperature, in K
g = 9.80665 # Gravity in m/s^2
L = 6.5     # Temp lapse rate in K/km
R = 8.31432 # Gas constant, J/mol*K
M = 28.9644 # Molecular weight of dry air, g/mol

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

# Returns air density in g/m^3given pressure in mb, temp in K, and rh
def density(press, temp, rh):
# from https://wahiduddin.net/calc/density_altitude.htm
    tc = temp - 273.15
    c0 = 6.1078
    c1 = 7.5
    c2 = 237.3
    Es = c0 * 10 ** (c1*tc/(c2+tc))
    pv = rh * Es * 100 # Water vapor press in Pa
    pd = press*100 - pv # Dry air pressure in Pa

    Rd = 287.05 # gas constant for dry air, J/(kg*K)
    Rv = 461.495 # gas constant for water vapor, J/(kg*K)
    d = pd/(Rd*temp) + pv/(Rv*temp) # air density, kg/m^3
    return d*1000 # g/m^3

# returns geopotential density altitude in km given air density in g/m^3
def density_alt(d):
# from https://wahiduddin.net/calc/density_altitude.htm
    return (T0/L) * (1 - (R*T0*d/(M*P0)) ** (L*R/(g*M-L*R)) )

# returns geometric altitude in km given geopotential altitude in km
def geopotential_to_geometric(alt):
    E = 6356.766 # Radius of earth, in km
    return E*alt / (E-alt)

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
        if g.name == "Geopotential Height" and g.typeOfLevel == "isobaricInhPa":
            hght_grib.append(g)
    grib.rewind()
    return sorted(hght_grib, key=level_key, reverse=True)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reverse Density Altitude Calculator: calculate the altitude MSL at which the density altitude is equal to the specified density altitude in current conditions, as specified by the HRRR model. Useful for calculating an aircraft's effective service ceiling in non-standard conditions")
    parser.add_argument("DA", help="Desired density altitude")
    parser.add_argument("lat", help="Latitude")
    parser.add_argument("lon", help="Longitude")
    parser.add_argument("--grib-file", type=str, default=None, help="Grib or Grib2 file to use; will download latest HRRR if not specified")
    parser.add_argument("--hour", type=int, default=1, help="Which hour to consider, from one hour ago (default 1)")

    args = parser.parse_args()
    if args.grib_file is None:
        download = True
        clean_up = True

    # Downlaod HRRR files for forecast hours 0-3
    for fh in range(0, 3+1):
        if download:
            local_hrrr_fn = download_hrrr_prsf(fh)
        else:
            local_hrrr_fn = args.grib_file
        # HRRR pressure field files are pretty large, so extract what is needed from each then remove it
        grib = pygrib.open(hrrr_fn)
        temp_grib = get_temp_grib(grib)
        hght_grib = get_hght_grib(grib)
        rh_grib = get_rh_grib(grib)

        if clean_up:
            os.remove(local_hrrr_fn)
