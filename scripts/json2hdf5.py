import argparse
import os
import glob
import lpl_weather
import json
from tqdm import tqdm

p = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
p.add_argument("--station", "-s", help="station to convert", default="KCALIVER78")
p.add_argument("--root", "-r", help="root path", default=os.path.expanduser("~/Weather/history"))
p.add_argument("--json", "-j", help="pattern to select json via glob", default="*.json")
p.add_argument("--force", "-f", help="force write hdf5 file", action="store_true")


args = p.parse_args()

print(args.station, args.root)

pth = os.path.join(args.root, args.station)

files = glob.glob(os.path.join(pth, args.json))

pbar = tqdm(files)
for fnm in pbar:
    pbar.set_description(fnm)
    if os.path.exists(fnm[:-4]+"hdf5"):
        if not args.force:
            continue
    with open(fnm) as f:
        data = json.load(f)
    data_dict = lpl_weather.utils.samples_to_numpy(data["observations"])
    lpl_weather.utils.numpy_to_hdf5(data_dict, pth)