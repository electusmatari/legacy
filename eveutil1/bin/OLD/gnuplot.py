import csv
import datetime
import subprocess

class Gnuplot(object):
    def __init__(self, title, xlabel, ylabel, outfile):
        self.gnuplot = subprocess.Popen(["gnuplot"],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
        self.set("title", '"%s"' % title)
        self.set("xlabel", '"%s"' % xlabel)
        self.set("ylabel", '"%s"' % ylabel)
        self.set("xdata", "time")
        self.set("timefmt", '"%Y-%m-%d"')
        self.set("format", 'x "%Y-%m-%d"')
        self.set("term", "png size 800, 600")
        self.set("grid")
        self.set("output", '"%s"' % outfile)

    def cmd(self, s):
        self.gnuplot.stdin.write(s + "\n")
        
    def set(self, name, value=""):
        self.cmd("set %s %s" % (name, value))

    def add_arrow(self, day, label, pos=0.9, duration=None, linetype=3):
        self.set("arrow",
                 ('from "%s", graph 0 to "%s", graph 1 back nohead linetype %i'
                  % (day, day, linetype)))
        self.set("label",
                 ('" %s" at "%s", graph %s front'
                  % (label, day, pos)))
        if duration is not None:
            endday = (datetime.datetime.strptime(day, "%Y-%m-%d") +
                      datetime.timedelta(days=duration)).strftime("%Y-%m-%d")
            self.set("arrow",
                     ('from "%s", graph %s to "%s", graph %s head linetype %i'
                      % (day, pos - 0.02, endday, pos - 0.02, linetype)))

    def add_bar(self, start, end, label, pos=0.5, linetype=3):
        if end is None:
            end = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        self.set("arrow",
                 ('from "%s", graph %s to "%s", graph %s front head linetype %i'
                  % (start, pos, end, pos, linetype)))
        self.set("label",
                 ('"%s" at "%s", graph %s front'
                  % (label, start, pos - 0.015)))

    def mplot(self, entries, start=None):
        if start is None:
            start = entries[0][1][0][0]
        self.set("xrange", '["%s":"%s"]' % (start,
                                            entries[0][1][-1][0]))
        args = []
        datasets = []
        for (title, data) in entries:
            args.append('"-" using 1:2 with lines title "%s"' % title)
            datasets.append(data)
        self.cmd('plot %s' % ", ".join(args))
        for data in datasets:
            csv.writer(self.gnuplot.stdin, delimiter="\t").writerows(data)
            self.gnuplot.stdin.write("e\n")

    def plot(self, title, data):
        self.set("xrange", '["%s":"%s"]' % (data[0][0],
                                            data[-1][0]))
        self.cmd('plot "-" using 1:2 with lines title "%s"' % title)
        csv.writer(self.gnuplot.stdin, delimiter="\t").writerows(data)
        self.gnuplot.stdin.write("e\n")
