#!/usr/bin/python

import cgitb
cgitb.enable()

import sys
import csv
import cgi
import MySQLdb

secret = "or else"

db_host = "localhost"
db_user = "emcom"
db_pass = "ai5ahNgi"
db_name = "emkillboard"

em_ally = 48

query = """
SELECT k.kll_timestamp, sys.sys_name, reg.reg_name, k.kll_all_id, k.kll_crp_id, ships.shp_name
FROM kb3_kills AS k
     INNER JOIN kb3_systems AS sys
       ON k.kll_system_id = sys.sys_id
     INNER JOIN kb3_constellations AS const
       ON sys.sys_con_id = const.con_id
     INNER JOIN kb3_regions AS reg
       ON const.con_reg_id = reg.reg_id
     INNER JOIN kb3_ships AS ships
       ON k.kll_ship_id = ships.shp_id
     INNER JOIN kb3_ship_classes AS cls
       ON ships.shp_class = cls.scl_id
WHERE (k.kll_all_id = 48
       OR 48 IN (SELECT ind_all_id FROM kb3_inv_detail
                 WHERE ind_kll_id = kll_id AND ind_plt_id != 44292))
      OR (k.kll_timestamp > '2009-12-10'
          AND k.kll_timestamp < '2010-01-17'
          AND ((k.kll_crp_id = 1232
                OR 1232 IN (SELECT ind_crp_id FROM kb3_inv_detail
                   WHERE ind_kll_id = kll_id))
                OR (k.kll_crp_id = 8974
                    OR 8974 IN (SELECT ind_crp_id FROM kb3_inv_detail
                       WHERE ind_kll_id = kll_id))
                OR (k.kll_crp_id = 8275
                    OR 8275 IN (SELECT ind_crp_id FROM kb3_inv_detail
                       WHERE ind_kll_id = kll_id))
                ))
ORDER BY k.kll_timestamp;
"""

ship_cls_translation = {
#    "Battleship": "Battleship",
#    "Capsule": "Civilian",
    "Noobship": "Rookie ship",
#    "Frigate": "Civilian",
#    "Interceptor": "Frigate II",
#    "Assault frigate": "Frigate II",
#    "Industrial": "Civilian",
#    "Cruiser": "Cruiser",
#    "Heavy assault": "Cruiser II",
#    "Battlecruiser": "Battlecruiser",
#    "Shuttle": "Civilian",
#    "Mining barge": "Civilian",
#    "Logistics": "Cruiser II",
#    "Transport": "Civilian",
#    "Destroyer": "Frigate",
#    "Covert ops": "Frigate II",
#    "Drone": "Unknown",
#    "Unknown": "Unknown",
#    "Dreadnought": "Capital",
#    "Freighter": "Civilian",
#    "Command ship": "Battlecruiser II",
#    "Exhumer": "Civilian",
#    "Interdictor": "Frigate II",
#    "Recon ship": "Cruiser II",
#    "Titan": "Capital",
#    "Carrier": "Capital",
#    "Mothership": "Capital",
#    "Cap. Industrial": "Capital",
#    "Electronic Attack Ship": "Frigate II",
#    "Heavy Interdictor": "Cruiser II",
#    "Black Ops": "Battleship II",
#    "Marauder": "Battleship II",
#    "Jump Freighter": "Capital",
    }

ship_cls_values = {
    "Battleship": 8,
    "Capsule": 0.5,
    "Noobship": 0.5,
    "Frigate": 1,
    "Interceptor": 2,
    "Assault frigate": 2,
    "Industrial": 1,
    "Cruiser": 2,
    "Heavy assault": 4,
    "Battlecruiser": 4,
    "Shuttle": 0.5,
    "Mining barge": 1,
    "Logistics": 4,
    "Transport": 2,
    "Destroyer": 1,
    "Covert ops": 2,
    "Drone": 0,
    "Unknown": 0,
    "Dreadnought": 16,
    "Freighter": 8,
    "Command ship": 8,
    "Exhumer": 0.5,
    "Interdictor": 2,
    "Recon ship": 4,
    "Titan": 32,
    "Carrier": 16,
    "Mothership": 32,
    "Cap. Industrial": 8,
    "Electronic Attack Ship": 2,
    "Heavy Interdictor": 4,
    "Black Ops": 16,
    "Marauder": 16,
    "Jump Freighter": 8,
    }

warzone = [u'Amamake', u'Anka', u'Arayar', u'Ardar', u'Arnher', u'Arnstur',
           u'Arzad', u'Aset', u'Asghed', u'Auga', u'Auner', u'Avenod',
           u'Bosboger', u'Brin', u'Dal', u'Ebolfer', u'Egmar', u'Eszur',
           u'Evati', u'Eytjangard', u'Ezzara', u'Floseswin', u'Frerstorn',
           u'Gebuladi', u'Gukarla', u'Gulmorogod', u'Hadozeko', u'Halmah',
           u'Haras', u'Helgatild', u'Hofjaldgund', u'Huola', u'Iesa',
           u'Isbrabata', u'Kamela', u'Klogori', u'Kourmonen', u'Kurniainen',
           u'Labapi', u'Lamaa', u'Lantorn', u'Lasleinur', u'Lulm', u'Ofstold',
           u'Ontorn', u'Orfrold', u'Oyeman', u'Oyonata', u'Raa', u'Resbroko',
           u'Roushzar', u'Sahtogas', u'Saidusairos', u'Saikamon', u'Sifilar',
           u'Sirekur', u'Siseide', u'Sosala', u'Sosan', u'Taff', u'Tannakan',
           u'Tararan', u'Todifrauan', u'Turnur', u'Tzvi', u'Ualkin',
           u'Uisper', u'Uusanen', u'Vard', u'Vimeini']

def main():
    form = cgi.FieldStorage()
    password = form.getfirst("password", None)
    if password is None:
        do_form()
    elif password != secret:
        do_form("<b>Wrong password.</b>")
    else:
        do_csv()

def do_form(msg=""):
    print "Content-Type: text/html"
    print
    print "<html><body>"
    print msg
    print '<form method="post" action="killexport.cgi">'
    print '<input type="password" name="password">'
    print '<input type="submit">'
    print '</form>'

def do_csv():
    db = MySQLdb.connect(host=db_host, user=db_user,
                         passwd=db_pass, db=db_name)
    c = db.cursor()
    c.execute(query)
    print "Content-Type: text/plain"
    print
    w = csv.writer(sys.stdout)
    for (time, system, region, ally, corp, ship_cls) in c.fetchall():
        # FW corps
        if ally == 48 or corp in (1232, 8974, 8275, 5305):
            ktype = "loss"
        else:
            ktype = "kill"
        if ship_cls in ship_cls_values:
            ship_value = ship_cls_values[ship_cls]
        else:
            ship_value = 0.5
        if ship_cls in ship_cls_translation:
            ship_cls = ship_cls_translation[ship_cls]
        if system in warzone:
            is_warzone = True
        else:
            is_warzone = False
        time = str(time)
        (date, time) = time.split(" ")
        w.writerow((date, time, region, ktype, ship_cls, ship_value, is_warzone))

main()
