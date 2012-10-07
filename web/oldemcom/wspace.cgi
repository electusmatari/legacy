#!/usr/bin/env python

import cgitb ; cgitb.enable()
import cgi
import pickle
import math

PICKLEFILE = "/home/forcer/Projects/old-emcom/ftp/data/wspace.pickle"

pator_x = -9.35790295622701e+16
pator_y = 4.37806703802814e+16
pator_z = -5.6561954432336e+16

form = cgi.FieldStorage()

def main():
    print "Content-Type: text/html"
    print
    q = form.getfirst("q", None)
    print HTML_HEADER
    if q is not None:
        q = q.upper()
        (whole, wsystem) = pickle.load(file(PICKLEFILE))
        if q in wsystem:
            (sysclass, anomaly, x, y, z) = wsystem[q]
            dist = math.sqrt((x - pator_x)**2 +
                             (y - pator_y)**2 +
                             (z - pator_z)**2)
            effects = anomaly_effects(anomaly)
            print HTML_SYSTEM % {"name": q,
                                 "class": class_explain(int(sysclass)),
                                 "anomaly": anomaly,
                                 "effects": "<br />".join(effects),
                                 "distance": distance(dist)}
        elif q in whole:
            (max_stab, max_mass, max_reg, max_jump_mass, sysclass, dist) = whole[q]
            print HTML_WHOLE % {"name": q,
                                "max_stab": time(float(max_stab)),
                                "max_mass": mass(float(max_mass)),
                                "max_reg": humane(float(max_reg)),
                                "max_jump_mass": mass(float(max_jump_mass)),
                                "class": class_explain(int(float(sysclass))),
                                "dist": dist}
        elif q == "K162":
            print HTML_WHOLE_K162
        else:
            print "<p>Query not found.</p>"
    print HTML_FOOTER

def anomaly_effects(a):
    if a == 'Pulsar':
        return (green('better shield amount'),
                green('better targeting range'),
                green('better cap recharge'),
                red('worse signature size'),
                red('worse armor resists'))
    elif a == 'Black Hole':
        return (green('better ship velocity'),
                green('better inertia modifier'),
                red('worse missile velocity'),
                red('worse drone control range'),
                red('worse optimal range'),
                red('worse falloff'))
    elif a == 'Cataclysmic Variable':
        return (green('better local shield boost'),
                green('better remote armor repair'),
                green('better capacitor capacity'),
                red('worse remote shield boost'),
                red('worse local armor repair'),
                red('worse capacitor recharge'))
    elif a == 'Magnetar':
        return (green('better ECM/TD/damp/TP'),
                green('better damage'),
                red('worse drone velocity'),
                red('worse targeting range'),
                red('worse tracking speed'),
                #red('worse AOE velocity')
                )
    elif a == 'Red Giant':
        return (green('better smart bomb range'),
                green('better smart bomb damage'),
                green('better overload bonus'),
                red('worse heat damage'))
    elif a == 'Wolf-Rayet Star':
        return (green('better armor resists'),
                green('better small weapon damage'),
                green('better signature radius'),
                red('worse shield resists'))
    else:
        return []
        
def red(s):
    return '<font color="#FF0000">%s</font>' % s

def green(s):
    return '<font color="#00FF00">%s</font>' % s

def time(t):
    if t < 60:
        return humane(t) + " min"
    elif t < 60*24:
        return humane(t/60) + " hr"
    else:
        return humane(t/(60*24)) + " d"

def mass(m):
    if m > 1000000:
        return humane(m/1000000) + " M kg"
    else:
        return humane(m) + " kg"

def distance(d):
    return humane(d / 9.4605284e15) + " ly"

def humane(obj):
    if isinstance(obj, int):
        return humane_int(obj)
    elif isinstance(obj, float):
        return humane_float(obj)
    else:
        return obj

def class_explain(c):
    if c == 9:
        return '9 (zero-sec)'
    elif c == 8:
        return '8 (low-sec)'
    elif c == 7:
        return '7 (high-sec)'
    elif c in (5, 6):
        return '%s (deadly space)' % c
    elif c in (3, 4):
        return '%s (dangerous space)' % c
    elif c in (1, 2):
        return '%s (unknown space)' % c
    else:
        return c

def humane_float(num):
    num = "%.2f" % float(num)
    return humane_int(num[:-3]) + num[-3:]

def humane_int(num):
    num = str(int(num))
    if num[0] == "-":
        sign = "-"
        num = num[1:]
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

HTML_HEADER = """
<html>
  <header>
    <title>Electus Matari Exploration Database</title>
  </header>
  <body>
    <h1>Electus Matari Exploration Database</h1>
    <form method="get" action="/wspace.cgi">
      <input type="text" name="q" />
      <input type="submit" />
    </form>
"""

HTML_FOOTER = """
  </body>
</html>
"""

HTML_SYSTEM = """
<h2>Locus Signature %(name)s</h2>
<ul>
  <li>Class: %(class)s</li>
  <li>Distance to Pator: %(distance)s</li>
  <li>Anomaly: %(anomaly)s<br />%(effects)s</li>
</ul>
"""

HTML_WHOLE = """
<h2>Wormhole %(name)s</h2>
<ul>
  <li>Maximum Stability Window: %(max_stab)s</li>
  <li>Maximum Mass Capacity: %(max_mass)s</li>
<!--  <li>Mass Regeneration: %(max_reg)s</li> -->
  <li>Maximum Jumpable Mass: %(max_jump_mass)s</li>
  <li>Target System Class: %(class)s</li>
<!-- <li>Target Distribution ID: %(dist)s</li> -->
</ul>
"""

HTML_WHOLE_K162 = """
<h2>Wormhole K162</h2>
<p>For any two connected wormholes, one end is always identified as K162.</p>
"""

main()
