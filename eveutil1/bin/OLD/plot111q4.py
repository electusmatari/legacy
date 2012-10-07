import sys
sys.path.append("/home/forcer/Projects/eveutil/dev/bin")

import csv
import datetime

from collections import defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib import dates
from matplotlib.patches import FancyArrowPatch

def main():
    days = 7
    fullhistory(days, '/home/forcer/public_html/em-kills-111Q4.png')
    fullhistory(days, '/home/forcer/public_html/em-kills-1st-111Q4.png',
                aboutshift=1)
    fullhistory(days, '/home/forcer/public_html/em-kills-2nd-111Q4.png',
                aboutshift=2)
    fullhistory(days, '/home/forcer/public_html/em-kills-3rd-111Q4.png',
                aboutshift=3)

def fullhistory(days, outfile, aboutshift=None):
    fig = plt.figure()
    kplt = fig.add_subplot(111)

    if aboutshift is None:
        select = lambda time: True
    else:
        select = shift(aboutshift)

    kpdra = getkills("2006-08-20", days, 
                     lambda ts, kpd, lpd: kpd.get(ts, 0),
                     select=select)
    lpdra = getkills("2006-08-20", days,
                     lambda ts, kpd, lpd: lpd.get(ts, 0),
                     select=select)
    def efficiency(ts, kpd, lpd):
        if kpd.get(ts, 0) == 0:
            if lpd.get(ts, 0) == 0:
                return None
            else:
                return 0
        else:
            return kpd[ts] / float(kpd[ts] + lpd.get(ts, 0))
    epdra = getkills("2006-08-20", days, efficiency,
                     select=select)

    yl = dates.WeekdayLocator(byweekday=0)
    ml = dates.DayLocator()
    kplt.xaxis.set_major_locator(yl)
    kplt.xaxis.set_minor_locator(ml)
    kplt.xaxis.set_major_formatter(dates.DateFormatter("%m-%d"))
    kplt.set_xlabel('Time')
    kplt.set_ylabel('Kills')
    kplt.set_autoscale_on(False)
    if aboutshift is None:
        kplt.set_ylim(0, 25)
        pass
    else:
        kplt.set_ylim(0, 10)
        pass
    kplt.grid(True)

    eplt = kplt.twinx()
    eplt.set_autoscale_on(False)
    eplt.xaxis.set_major_locator(yl)
    eplt.xaxis.set_minor_locator(ml)
    eplt.xaxis.set_major_formatter(dates.DateFormatter("%m-%d"))
    eplt.set_yticks([0, 0.5, 1])
    eplt.set_ylim(0, 6)
    eplt.set_ylabel('Efficiency')
    eplt.axhline(y=0.5, color='r', alpha=0.5)

    def longwar(start, end, label, pos=0, color="k"):
        smallskip = 0.05
        bigskip = 0.5
        yst = 4.5
        ax = eplt
        (_, xmax) = ax.get_xlim()
        start = dates.date2num(d(start))
        if end is None:
            end = xmax
        else:
            end = dates.date2num(d(end))
        ax.annotate(label, (start, yst-bigskip*pos), alpha=0.8)
        ax.add_patch(FancyArrowPatch((start, (yst-smallskip)-bigskip*pos),
                                     (end, (yst-smallskip)-bigskip*pos),
                                     color=color,
                                     arrowstyle="->",
                                     mutation_scale=30,
                                     alpha=0.5
                                     ))
        plt.axvline(start, color=color, linestyle="-", alpha=0.3)
        plt.axvline(end, color=color, linestyle="-", alpha=0.3)

    longwar("2009-10-10", "2009-10-28", "PODLA conflicts", pos=1, color="r")
    longwar("2009-10-27", "2009-11-04", "EXALT war", pos=0, color="r")
    longwar("2009-11-01", "2009-11-06", "Privateer wars", pos=1)
    longwar("2009-11-08", "2009-11-27", "", pos=1)
    longwar("2009-11-11", "2009-11-18", "DEMON war", pos=0, color="c")
    longwar("2009-12-11", "2010-01-17", "Militia", 2)

    kplt.plot([x[0] for x in kpdra],
              [x[1] for x in kpdra],
              'g-', label="Kills")
    kplt.plot([x[0] for x in lpdra],
              [x[1] for x in lpdra],
              'r-', label="Losses")
    eplt.plot([x[0] for x in epdra],
              [x[1] for x in epdra],
              'b-', label="Efficiency")
    kplt.legend(loc='upper left')
    mvgstart = datetime.datetime.strptime("2009-10-01", "%Y-%m-%d")
    kplt.set_xlim(xmin=mvgstart, xmax=kpdra[-1][0])
    eplt.set_xlim(xmin=mvgstart, xmax=kpdra[-1][0])
    fig.savefig(outfile, width=800, height=600)

def getkills(start, days, f,
             getvalue=lambda shiptype, value: 1,
             select=lambda x: True):
    killlist = list(csv.reader(file("em-kills.txt")))
    kpd = defaultdict(lambda: 0)
    lpd = defaultdict(lambda: 0)
    for (day, time, region, killorloss, ship, value, republic) in killlist:
        if select(time):
            if killorloss == 'kill':
                kpd[day] += getvalue(ship, float(value))
            else:
                lpd[day] += getvalue(ship, float(value))
    killdata = {}
    start = datetime.datetime.strptime(killlist[0][0], "%Y-%m-%d")
    end = datetime.datetime.strptime(killlist[-1][0], "%Y-%m-%d")
    inc = datetime.timedelta(days=1)
    now = start
    while now <= end:
        nowiso = now.strftime("%Y-%m-%d")
        killdata[nowiso] = f(nowiso, kpd, lpd)
        now += inc
    kpd = killdata.items()
    kpd.sort()
    kpdra = zip([datetime.datetime.strptime(x[0], "%Y-%m-%d") for x in kpd],
                raverage([x[1] for x in kpd], days))
    return kpdra

def raverage(seq, n):
    result = []
    for i in range(0, len(seq)):
        subseq = [x for x in seq[max(0, (i-n)):i]
                  if x is not None]
        if len(subseq) == 0:
            result.append("NaN")
        else:
            result.append(sum(subseq) / float(len(subseq)))
    return result

def shift(s):
    def is_time(time):
        hour = int(time.split(":")[0])
        if hour >= 6 and hour < 14:
            shift = 1
        elif hour >= 14 and hour < 22:
            shift = 2
        elif hour >= 22 or hour < 6:
            shift = 3
        else:
            raise RuntimeException, "Bad hour %i" % hour
        return shift == s
    return is_time

def d(date):
    return datetime.datetime.strptime(date, "%Y-%m-%d")

if __name__ == '__main__':
    main()
