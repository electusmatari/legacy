# em.com FTP uploader

import ftplib

def upload(fname, uploadfile, account='deliveries',
           directory=None):
    f = file("/home/forcer/.private.txt")
    lines = [line.strip().split(":") for line in f.readlines()]
    pws = dict((s, (u, p)) for (s, u, p) in lines)
    (u, p) = pws[account]
    ftp = ftplib.FTP('www.electusmatari.com')
    ftp.login(u, p)
    if directory is not None:
        ftp.cwd(directory)
    ftp.storbinary("STOR %s" % (fname,), uploadfile)
    ftp.quit()

def uploadmany(files, account='deliveries', directory=None):
    f = file("/home/forcer/.private.txt")
    lines = [line.strip().split(":") for line in f.readlines()]
    pws = dict((s, (u, p)) for (s, u, p) in lines)
    (u, p) = pws[account]
    ftp = ftplib.FTP('www.electusmatari.com')
    ftp.login(u, p)
    if directory is not None:
        ftp.cwd(directory)
    for filename, uploadfile in files:
        ftp.storbinary("STOR %s" % (filename,), uploadfile)
    ftp.quit()
