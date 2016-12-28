from distutils.core import setup

setup (name = "weather",
       author="Charles Doutriaux"
       version=0.9,
       description = "Utilities to read back in my weather station data".
       packages = ['weather'],
       package_dir = {'weather': 'src'},
       #data_files = [ ("share/weather",())],
      )
