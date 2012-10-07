def eve_time(time=None):
    if time is None:
        time = datetime.datetime.utcnow()
    try:
        t = time.strftime("%m.%d %H:%M:%S")
        y = time.year - 1898
        return "%3i.%s" % (y, t)
    except:
        return "never"

def humane(obj, dosign=False):
    if isinstance(obj, int) or isinstance(obj, long):
        return humaneint(obj, dosign)
    elif isinstance(obj, float):
        return humanefloat(obj, dosign)
    else:
        return obj

def humanefloat(num, dosign):
    # -0.23 results in humaneint("-0") ...
    if num < 0:
        dominus = True
    else:
        dominus = False
    num = "%.2f" % float(num)
    res = humaneint(num[:-3], dosign) + num[-3:]
    if dominus:
        return "-" + res.lstrip("-")
    else:
        return res

def humaneint(num, dosign):
    num = str(long(num))
    if num[0] == "-":
        sign = "-"
        num = num[1:]
    elif dosign:
        sign = "+"
    else:
        sign = ""
    triple = []
    while True:
        if len(num) > 3:
            triple = [num[-3:]] + triple
            num = num[:-3]
        else:
            triple = [num] + triple
            break
    return sign + ",".join(triple)

def showinfo(text, typeid, itemid=None):
    if itemid is None:
        return '<span style="color: blue; text-decoration: underline; cursor: pointer" onClick="CCPEVE.showInfo(%s)">%s</span>' % (typeid, text)
    else:
        return '<span style="color: blue; text-decoration: underline; cursor: pointer" onClick="CCPEVE.showInfo(%s, %s)">%s</span>' % (typeid, itemid, text)
