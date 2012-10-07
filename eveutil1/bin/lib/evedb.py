import psycopg2

def connect(dbname="eve"):
    return psycopg2.connect("host=localhost dbname=%s user=forcer" % dbname)
