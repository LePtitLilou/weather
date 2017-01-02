import json
import numpy
import cdtime
import cdms2
import requests
import os

cdms2.setNetcdfDeflateFlag(0)
cdms2.setNetcdfDeflateLevelFlag(0)
cdms2.setNetcdfShuffleFlag(0)

# Weather underground UTZ ref date (epoch)
ref_date = cdtime.comptime(1970)

units = {
    "temperature": "degF",
    "precip": "in",
    "precip_rate": "in/hr",
    "pressure": "inHg",
}


def mean(x, y, ref_units, rk=7, dx=60.):
    t1 = cdtime.reltime(x[0], units)
    t1c = t1.tocomp()
    t0 = cdtime.comptime(t1c.year, t1c.month, t1c.day).torel(units).value
    te = cdtime.comptime(
        t1c.year, t1c.month, t1c.day).add(
        1, cdtime.Day).torel(units).value
    X = x - float(t0)
    poly = numpy.polyfit(X, y, rk)
    P = numpy.poly1d(poly)
    ys = []
    i = 0
    while i <= (te - t0):
        ys.append(P(i))
        i += dx
    return numpy.trapz(ys, dx=dx) / (te - t0)


def retrieve(obs, variable):
    x = []
    y = []
    # 59.6 F is weather underground average for Feb 26th, 2016
    for o in obs:
        try:
            t = float(o[variable])
            x.append(float(o["date"]["epoch"]))
            y.append(t)
        except:
            pass
    return numpy.array(x), numpy.array(y)


def mystation(year):
    if year < 2016:
        station = "KCALIVER55"
    else:
        station = "KCALIVER78"
    return station


def day2cdms(year, month, day, variables=["temperature"], station=None):
    print("\tProcessing: %.4i-%.2i-%.2i" % (year, month, day))
    if isinstance(variables, basestring):
        variables = [variables]
    date = "%.4i%.2i%.2i" % (year, month, day)
    fname = date + ".json"
    if station is None:
        station = mystation(year)
    fname = os.path.join("history", station, fname)
    if not os.path.exists(fname):  # No data aborting
        print("\t\tNo json")
        return []
    f = open(fname)
    data = json.load(f)
    f.close()
    tz_offset_hours = data["response"]["date"]["tz_offset_hours"]
    ref = ref_date.add(tz_offset_hours, cdtime.Hours)
    ref_units = "seconds since %s" % str(ref)
    history = data["history"]["days"]
    if len(history) == 0:  # no data in file
        print("\t\tNo Data in JSON")
        return []
    obs = history[0]["observations"]
    out = []
    for v in variables:
        x, y = retrieve(obs, v)
        if v == variables[0]:
            tim = cdms2.createAxis(numpy.array(x))
            tim.units = ref_units
            tim.designateTime()
            tim.id = "time"
        y = cdms2.MV2.array(y)
        y.setAxis(0, tim)
        y.id = v
        y.units = units[v]
        out.append(y)
    print("\t\tNumber of records: %i" % len(x))
    return out


def month2cdms(year, month, variables=["temperature"], station=None):
    if station is None:
        station = mystation(year)
    out = "%.4i%.2i_%s.nc" % (year, month, station)
    print("Out file:", out)
    f = cdms2.open(out, "w")
    day = cdtime.comptime(year, month)
    while day.month == month:
        day_var = day2cdms(year, month, day.day, variables, station)
        if day_var == []:  # No data
            day = day.add(1, cdtime.Day)
            continue
        for v in day_var:
            f.write(v)
        day = day.add(1, cdtime.Day)
    f.close()


def get_history(year, month, day, station_id=None, pathout=None, key=None):
    if station_id is None:
        station_id = mystation(year)
    if key is None:
        key = "606f3f6977348613"
    date = "%.4i%.2i%.2i" % (year, month, day)
    if pathout is None:
        pathout = os.path.join(os.path.expanduser("~/"), "Weather", "history")
    name = os.path.join(pathout, station_id, date + ".json")
    f = open(name, "w")
    url = "https://api-ak.wunderground.com/api/%s/history_%s/units:english/v:2.0/q/pws:%s.json" % (
        key, date, station_id)
    r = requests.get(url)
    f.write(r.content)
    f.close()
    if not r.status_code == 200:
        print "\t\t Failed", r.status_code
        os.remove(name)
        return
    else:
        print "\t\t Success"
    return name
