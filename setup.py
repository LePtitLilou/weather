from setuptools import setup

setup (name = "lpl_weather",
       author="Charles Doutriaux",
       version="0.9",
       description = "Utilities to read back in my weather station data",
       packages = ['lpl_weather'],
       scripts = ["scripts/json2hdf5.py",],
       # data_files = [ ("share/weather",())],
      )
