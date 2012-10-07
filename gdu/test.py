#!/usr/bin/env python

import os
import subprocess
import time

os.chdir("data")
os.environ["PATH"] += "C:\\Python27"
os.environ["PYTHONPATH"] = "..\\lib"
retcode = subprocess.call(["python", "..\\scripts\\gdu.py"])
if retcode != 0:
    time.sleep(60)
