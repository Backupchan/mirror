#!/usr/bin/python3

import configtony
import os
import sys
import time
import logging
import logging.handlers
from mirror import Mirror

#
# Setting up logging
#

if not os.path.exists("./log"):
    os.mkdir("./log")

formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s]: %(message)s")

file_handler = logging.handlers.RotatingFileHandler("log/backupchan_mirror.log", maxBytes=2000000, backupCount=5)
file_handler.setFormatter(formatter)

console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

#
# Reading configuration
#

main_config = configtony.Config("config.jsonc")
main_config.add_option("check_interval", int, 7200)
main_config.add_option("save_path", str, "/var/backup_mirror")
main_config.add_option("connection", dict, {})
main_config.parse()

if main_config.get("connection") == {}:
    print("Please configure connection to the server.", file=sys.stderr)
    sys.exit(1)

target_config = configtony.Config("targets.jsonc")
target_config.add_option("targets", list, [])
target_config.parse()

if target_config.get("targets") == []:
    print("Please configure targets to mirror.", file=sys.stderr)
    sys.exit(1)

#
# Start mirroring
#

mirror = Mirror(main_config, target_config)
mirror.start()

while True:
    time.sleep(10)
