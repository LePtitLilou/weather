from distutils.core import setup

setup (name = "lpl_weather",
       author="Charles Doutriaux",
       version="0.1",
       description = "Utilities to read back in my weather station data",
       packages = ['lpl_weather'],
       package_dir = {'lpl_weather': 'src'},
       scripts = ["src/scripts/fetch_wu_station.py",],
       #data_files = [ ("share/weather",())],
      )
