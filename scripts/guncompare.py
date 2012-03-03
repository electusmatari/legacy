#!/usr/bin/env python

import emcom
import sys

def main():
    sec = 0
    if len(sys.argv) == 5:
        (ignored, volley1, rof1, volley2, rof2) = sys.argv
        delay1 = 0
        delay2 = 0
    elif len(sys.argv) == 7:
        (ignored, volley1, rof1, delay1, volley2, rof2, delay2) = sys.argv
    else:
        sys.stderr.write("usage: guncompare <volley1> <rof1> [delay1] <volley2> <rof2> [delay2]\n")
        sys.exit(1)
    rof1 = float(rof1)
    volley1 = float(volley1)
    delay1 = float(delay1)
    rof2 = float(rof2)
    volley2 = float(volley2)
    delay2 = float(delay2)
    dam1 = 0
    dam2 = 0
    next1 = delay1
    next2 = delay2
    print "| %-3s | %-10s %1s | %-10s %1s |" % ("Sec", "Ship 1", "",
                                                "Ship 2", "")
    print "|-%3s-|-%10s---|-%10s---|" % ("-"*3, "-"*10, "-"*10)
    for sec in xrange(0, 5*60):
        if sec >= next1:
            dam1 += volley1
            next1 += rof1
        if sec >= next2:
            dam2 += volley2
            next2 += rof2
        print "| %3s | %10s %1s | %10s %1s |" % (
            sec,
            emcom.humane(dam1),
            "!" if dam1 > dam2 else "",
            emcom.humane(dam2),
            "!" if dam2 > dam1 else "")


if __name__ == '__main__':
    main()
