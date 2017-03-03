#!/usr/bin/python
import argparse
import datetime
import numpy as np
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

# TODO replace this with scipy.interp1d after I get the internet back
# Find the point the same distance along [y0, y1] as x is along [x0, x1]
def interp1d(x0, x1, x, y0, y1):
    x_range = x1 - x0
    y_range = y1 - y0
    dx = x - x0
    x_frac = dx / x_range
    return x_frac * y_range + y0


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

def get_temp_grib(grib):
    temp_grib = []
    for g in grib:
        if g.name == "Temperature" and g.typeOfLevel == "isobaricInhPa":
            temp_grib.append(g)
    grib.rewind()
    return sorted(temp_grib, key=level_key, reverse=True)

def get_gph_grib(grib):
    gph_grib = []
    for g in grib:
        if g.name == "Geopotential Height" and g.typeOfLevel == "isobaricInhPa":
            gph_grib.append(g)
    grib.rewind()
    return sorted(gph_grib, key=level_key, reverse=True)

def get_rh_grib(grib):
    rh_grib = []
    for g in grib:
        if g.name == "Relative humidity" and g.typeOfLevel == "isobaricInhPa":
            rh_grib.append(g)
    grib.rewind()
    return sorted(rh_grib, key=level_key, reverse=True)

# Sort grib entries by level
def level_key(g):
    return g.level

# Returns the index of the closest point on a lat, lon grid to the specified lat, lon
def find_nearest_idx(shape, lats, lons, lat, lon):
    # for an unknown reason, pygrib gives lons and lats as 1-dimensional arrays, values as a 2-d array
    lats = np.reshape(lats, shape)
    lons = np.reshape(lons, shape)
    lons[lons>180] -= 360
    difflats = lats - lat
    difflons = lons - lon
    diffs = (difflats**2 + difflons**2)
    return np.where(diffs==np.min(diffs))

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

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Reverse Density Altitude Calculator: calculate the altitude MSL at which the density altitude is equal to the specified density altitude in current conditions, as specified by the HRRR model. Useful for calculating an aircraft's effective service ceiling in non-standard conditions. Default unit is feet; others may be specified as options.")
    parser.add_argument("DA", type=float, help="Desired density altitude")
    parser.add_argument("lat", type=float, help="Latitude")
    parser.add_argument("lon", type=float, help="Longitude")
    parser.add_argument("--grib-file", type=str, default=None, help="Grib or Grib2 file to use; will download latest HRRR if not specified")
    parser.add_argument("--hour", type=int, default=1, help="Which hour to consider, from one hour ago (default 1)")
    # TODO parse 'km' or 'm' from end of args.DA to determine unit
    parser.add_argument("--meters", "-m", action="store_true", help="Input and output in meters")
    parser.add_argument("--km", action="store_true", help="Input and output in meters")
    parser.add_argument("--print-units", "-u", action="store_true", help="Print units")
    parser.add_argument("--verbose", "-v", action="count", help="Be verbose")

    args = parser.parse_args()
    if args.grib_file is None:
        download = True
        clean_up = True
    else:
        download = False
        clean_up = False

    if download:
        local_hrrr_fn = download_hrrr_prsf(args.hour)
    else:
        local_hrrr_fn = args.grib_file
    grib = pygrib.open(local_hrrr_fn)
    temp_grib = get_temp_grib(grib)
    gph_grib = get_gph_grib(grib)
    rh_grib = get_rh_grib(grib)
    # HRRR files are large, so remove as soon as it's no longer needed
    if clean_up:
        os.remove(local_hrrr_fn)

    if args.km:
        unit = "km"
    elif args.meters:
        unit = "m"
    else:
        unit = "ft"
    if args.verbose >= 2:
        print "Press (mb) | Temp (C) | RH (%) | DA (gp {0:<2}) | MSL (gp {0:<2})".format(unit)
    if len(temp_grib) != len(gph_grib) or len(temp_grib) != len(rh_grib):
        raise IndexError("Temp, height, and humidity fields do not have same length!")
    idx = find_nearest_idx(temp_grib[0].values.shape,
            temp_grib[0].latitudes, temp_grib[0].longitudes,
            args.lat, args.lon)
    ix, iy = idx[0][0], idx[1][0]
    prev_da = None
    prev_gph = None
    done = False
    for i in range(len(temp_grib)):
        if temp_grib[i].level != rh_grib[i].level:
            raise ValueError("Temp/RH level mismatch!")
        level = temp_grib[i].level
        temp = temp_grib[i].values[ix][iy]
        rh = rh_grib[i].values[ix][iy] / 100.0
        if unit == "m":
            da = density_alt(density(level, temp, rh))*1000 #km to m
            gph = gph_grib[i].values[ix][iy]
            unit = "m"
        elif unit == "km":
            da = density_alt(density(level, temp, rh))
            gph = gph_grib[i].values[ix][iy] / 1000 # m to km
            unit = "km"
        else: # Default unit is feet
            da = density_alt(density(level, temp, rh))*3280 #km to ft
            gph = gph_grib[i].values[ix][iy] * 3.28 # m to ft
        if args.verbose >= 2:
            print "{:>10} | {:>8.3f} | {:>6.2f} | {:>10.1f} | {:>11.1f}".format(
                    level, temp-273.15, rh*100, da, gph)
        if da > args.DA and prev_da < args.DA:
            if prev_da is None:
                # TODO Is this the appropriate error type?
                raise ValueError("Unable to interpolate: specified density altitude below lowest found DA.")
            alt_fmt = "{0:<.5g}"
            da_str = alt_fmt.format(args.DA)
            interp_gph = interp1d(prev_da, da, args.DA, prev_gph, gph)
            gph_str = alt_fmt.format(interp_gph)
            if args.units:
                da_str += unit
                gph_str += unit
            done = True
            if args.verbose <= 1:
                break
        prev_da = da
        prev_gph = gph

    if done:
        if args.verbose >= 1:
            print "Interpolated GPH for {} density altitude: {}".format(da_str, gph_str)
        else:
            print gph_str

    else:
        raise ValueError("Unable to interpolate: specified density altitude above highest found DA.")

