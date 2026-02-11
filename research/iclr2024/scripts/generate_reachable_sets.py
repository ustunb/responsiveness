import argparse
import os

import psutil

settings = {
    "data_name": "german",
    "action_set_name": "complex_1D",
    "overwrite": True,
    "hard_cap": None,
}

ppid = os.getppid()
process_type = psutil.Process(ppid).name()  # e.g. pycharm, bash
if process_type not in ("pycharm"):
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_name", type=str, required=True)
    parser.add_argument("--action_set_name", type=str, required=True)
    parser.add_argument("--hard_cap", type=int, default=settings["hard_cap"])
    parser.add_argument(
        "--overwrite", default=settings["overwrite"], action="store_true"
    )
    args, _ = parser.parse_known_args()
    settings.update(vars(args))

from responsiveness.ext import fileutils
from responsiveness.paths import *

from responsiveness import ReachableSetDatabase

data = fileutils.load(get_data_file(**settings))
action_set = fileutils.load(get_action_set_file(**settings))
database_file = get_reachable_db_file(**settings)
print(f"db file: {get_reachable_db_file(**settings)}")
database = ReachableSetDatabase(action_set=action_set, path=database_file)
stats = database.generate(data.X, overwrite=settings["overwrite"])
print(stats.n_points.describe())
