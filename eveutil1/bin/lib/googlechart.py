import urllib

class GoogleChart(object):
    def __init__(self, cht="lc", chs="640x480"):
        self.args = [("cht", cht),
                     ("chs", chs)]
        self.data = []

    def add_data(self, data):
        self.data.append((minv, maxv, data))

    def set_lables(self, *labels):
        self.args.append(("chl", "|".join(labels)))

    def set_scaling(self, *args):
        """
        args is a list of numbers, interchangingly minv and maxv of
        each data set.
        """
        self.args.append(("chds", ",".join(args)))

    def get_url(self):
        args = self.args.copy()
        chds = []
            if minv and maxv:
                chds
        
        return ("http://chart.apis.google.com/chart" + "?" +
                urllib.urlencode(args))
