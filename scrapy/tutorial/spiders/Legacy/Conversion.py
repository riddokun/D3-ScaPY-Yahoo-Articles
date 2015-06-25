import time, datetime
import csv


class Conversion:
    def __init__(self):
        data = test("C:\lol\AP-2015-03-17.csv", header=None, delim_whitespace=True)
        mtime = data.value[:, 4]
        millis = int(round(time.time() * 1000))

        data.value[:,4] = datetime.datetime.fromtimestamp((millis - mtime * 60 * 1000)/1000).strftime('%m-%d-%Y %H:%M:%S.%f')
        data.to_csv("C:\lol\APNEW-2015-03-17.csv")
