import numpy
import h5py
import os
import json
import datetime
import glob
import time


def get_station_variable(station, variable="time5", files=None, root=os.path.expanduser("~/Weather/history")):
    if files is None:
        files = sorted(glob.glob(os.path.join(root, station, "*.hdf5")))
    out = None
    for f in files:
        h5 = h5py.File(f, "r")
        data = h5[variable]
        if out is None:
            out = data[:]
        else:
            out = numpy.concatenate((out,data[:]))
        h5.close()
    return out

def matching_times(s1, s2, return_indices=False):
    print("Reading in s1")
    times1 = get_station_variable(s1)
    print("ntimes 1:", len(times1), times1[:10])
    times2 = get_station_variable(s2)
    print("ntimes 2:", len(times2), times2[:10])
    return numpy.intersect1d(times1, times2, assume_unique=True, return_indices=return_indices)


def samples_to_numpy(data, variables = None):
    first = data[0]
    data_variables = first["imperial"].keys()
    if variables is None:
        variables = data_variables
    out = {}
    for var in variables:
        if not var in data_variables:
            raise("Variable {} is unavailable")
        out[var] = []
    out["times"]  = []
    out["epoch"]  = []
    out["station_id"] = first["stationID"] 
    for sample in data:
        out["times"].append(numpy.datetime64(sample["obsTimeLocal"]))
        out["epoch"].append(sample["epoch"])
        measurements = sample["imperial"]
        #print(measurements.keys())
        for v in variables:
            out[v].append(measurements[v])
            if out[v][-1] is None:
                out[v][-1] = -999
    for v in out:
        out[v] = numpy.array(out[v])
    return out

def to_datetime(date):
    """
    Converts a numpy datetime64 object to a python datetime object 
    Input:
      date - a np.datetime64 object
    Output:
      DATE - a python datetime object
    """
    timestamp = ((date - numpy.datetime64('1970-01-01T00:00:00'))
                 / numpy.timedelta64(1, 's'))
    return datetime.datetime.utcfromtimestamp(timestamp)


def numpy_to_hdf5(data,path = ".") :
    # figure out day
    time = to_datetime(data["times"][0])
    e5 = epoch_to_5minutes(data["epoch"])
    name = f"{time.year}{time.month:02d}{time.day:02d}.hdf5"
    with h5py.File(os.path.join(path, name), "w") as f:
        f["epoch"] = data["epoch"]/1000.
        f["time5"] = e5
        for v in data.keys():
            if v in ["times", "epoch"]:
                continue
            elif v == "station_id":
                f.station_id = data[v]
                continue
            f[v] = data[v]
            f[v].dims[0].label="time"
            f[v].dims[0].label="time5"


def epoch_to_5minutes(epochs):
    dt = [datetime.datetime.fromtimestamp(e/1000.) for e in epochs]
    e5 = []
    for d in dt:
        mn, sec = d.minute % 5, d.second / 60.
        dy = datetime.datetime(d.year, d.month, d.day, d.hour, d.minute - mn)
        if mn + sec > 2.5:
            dy = dy + datetime.timedelta(minutes=5)
        e5.append(dy)
    return [int(e.timestamp()) for e in e5]
