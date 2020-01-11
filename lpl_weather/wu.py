import json
import numpy
# import cdtime
# import cdms2
import requests
import os
import datetime
from tqdm.notebook import tqdm

# cdms2.setNetcdfDeflateFlag(0)
# cdms2.setNetcdfDeflateLevelFlag(0)
# cdms2.setNetcdfShuffleFlag(0)

# Weather underground UTZ ref date (epoch)
ref_date = datetime.date(1979, 1, 1)

units = {
    "temperature": "degF",
    "precip": "in",
    "precip_rate": "in/hr",
    "pressure": "inHg",
}


def mean(x, y, ref_units, rk=7, dx=60.):
    t1 = cdtime.reltime(x[0], ref_units)
    t1c = t1.tocomp()
    t0 = cdtime.comptime(t1c.year, t1c.month, t1c.day).torel(units).value
    te = cdtime.comptime(
        t1c.year, t1c.month, t1c.day).add(
        1, cdtime.Day).torel(ref_units).value
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


class PWS():
            # got key at: https://www.wunderground.com/member/api-keys
            # key = "06614bc862944b87a14bc86294db871b"
    def __init__(self, station_id=None,
                 units="e",  # or "m"
                 url="https://api.weather.com/v2/pws/history/{sampling}?stationId={station_id}&numericPrecision=decimal&format={format}&units={units}&date={date}&apiKey={key}",
                 # got this key in source dev of wunderground website
                 key="6532d6454b8aa370768e63d6ba5a832e",
                 sampling="all",  # "daily", "hourly"
                 force=True,
                 dump=True):
        self.station_id=station_id
        self.units = units
        self.url=url
        self.key=key
        self.force=force
        self.dump=dump
        self.sampling=sampling
        self.format = "json"

    def fetch_range(self, year1, month1, day1, year2 = None, month2 = None, day2 = None, pathout = None):
        """retrieve a range of days"""
        start=datetime.date(year1, month1, day1)
        today=datetime.date.today()
        if year2 is None:
            year2=today.year
        if month2 is None:
            month2=today.month
        if day2 is None:
            day2=tooday.day
        end=datetime.date(year2, month2, day2)
        day=datetime.timedelta(days = 1)
        delta= end - start
        if end < start:
            raise ValueError("End date must be greater than first date")

        fecthed=0
        for i in tdqm(range(delta.days)):
            try:
                name, _= self.fecth_day(start.year, start.month, start.day, pathout)
            except Exception as err:
                print("Failure for date:", start, err)
            if fetched == 1:
                print("First fetch:", name)
            start += day
        print("Last fetched:", name)
        print("Total fetched successfully:", fetched)
        print("Expected to fetch:", delta.days)

    def fetch_day(self, year = None, month = None, day = None, pathout = None):
        "download data for a day"
        today=datetime.date.today()

        if year is None:
            year=today.year
        if month is None:
            month=today.month
        if day is None:
            day=tooday.day

        station_id=self.station_id
        if station_id is None:
            station_id=mystation(year)

        date=f"{year}{month:02d}{day:02d}"

        if pathout is None:
            pathout=os.path.join(os.path.expanduser(
                "~/"), "Weather", "history", station_id)
        if not os.path.exists(pathout):
            os.makedirs(pathout)
        name=os.path.join(pathout, date + ".json")

        if not os.path.exists(name) or self.force:
            url = self.url.format(key=self.key, station_id=station_id, sampling=self.sampling, units=self.units, date=date, format=self.format)
            r=requests.get(url)
            if not r.status_code == 200:
                raise ConnectionError(f"\t\t Failed: {r.status_code}")
            data=r.json()
        else:
            with open(name) as f:
                data=json.load(f)
        if self.dump:
            with open(name, "w") as f:
                json.dump(data, f)
        print("\t\t Success")
        return name, data
