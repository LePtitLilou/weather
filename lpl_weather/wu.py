import json
import numpy
import requests
import os
import datetime
from tqdm.notebook import tqdm
import matplotlib.pyplot as plt
import h5py
from .utils import samples_to_numpy, numpy_to_hdf5  # noqa


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


def mystation(year):
    if year < 2016:
        station = "KCALIVER55"
    else:
        station = "KCALIVER78"
    return station


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
        self.tqdm = None
        self.ax = None
        self.fig = None


    def init_matplotlib(self):
        self.fig, self.ax = plt.subplots()
        self.ax.grid(True, linestyle="dotted", color="grey", linewidth=.5)

    def plot(self, x, y,
             color='blk',
             marker='o',
             ms=0,
             mfc=None,
             linestyle='solid',
             linewidth=1,
             mec=None,
             mew=1,
             overlay=False):
        if mfc is None:
            mfc = color
        if mec is None:
            mec = color
        w = numpy.argwhere(numpy.logical_not(numpy.equal(y,-999)))
        x = x[w][:,0]
        y = y[w][:,0]
        if not overlay:
            self.init_matplotlib()
        if self.ax is None:
            self.init_matplotlib()
        self.ax.plot(x,y,
                marker=marker, 
                linestyle=linestyle, 
                linewidth=linewidth,
                mfc=mfc,
                mec=mec,
                mew=mew,
                ms=ms,
                color=color, 
            )
        self.fig.autofmt_xdate()

    def fetch_range(self, start, end=None, pathout=None):
        """retrieve a range of days"""
        if end is None:
            end =datetime.date.today()
        day=datetime.timedelta(days = 1)
        delta= end - start
        if end < start:
            raise ValueError("End date must be greater than first date")

        fetched=0
        for i in tqdm(range(delta.days)):
            try:
                name, _ = self.fetch_day(start, pathout)
            except Exception as err:
                print("Failure for date:", start, err)
            if fetched == 1:
                print("First fetch:", name)
            start += day
        print("Last fetched:", name)
        print("Total fetched successfully:", fetched)
        print("Expected to fetch:", delta.days)

    def fetch_day(self, day = None, pathout = None):
        "download data for a day"

        if day is None:
            day=datetime.date.today()

        station_id=self.station_id
        if station_id is None:
            station_id=mystation(day.year)

        date=f"{day.year}{day.month:02d}{day.day:02d}"

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
        return name, data
