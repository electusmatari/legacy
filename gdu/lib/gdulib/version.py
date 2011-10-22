APPNAME = "GDU"
APPLONGNAME = "Gradient Data Uploader"
APPURL = "http://gradient.electusmatari.com/uploader/"
AUTH_TOKEN_URL = "http://gradient.electusmatari.com/uploader/token/"

VENDORNAME = "Gradient"
COPYRIGHT = "Copyright (C) 2011 Jorgen Schaefer"

VERSION = 1.0
VERSIONSTRING = "%.1f" % VERSION

DESCRIPTION = """\
The Gradient Data Uploader is a data mining tool that watches the
cache files of EVE Online clients for interesting data, extracts the
data, and uploads it to the Gradient website.\
"""

ABOUT = """\
%s v%s
Copyright (c) 2011 Jorgen Schaefer. All rights reserved.
(aka Arkady Sadik)

Released under the 2-clause BSD License.
""" % (APPLONGNAME, VERSIONSTRING)

LICENSE = """\
Copyright 2011 Jorgen Schaefer. All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:


   1. Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.

   2. Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.

THIS SOFTWARE IS PROVIDED BY JORGEN SCHAEFER ''AS IS'' AND ANY EXPRESS
OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL JORGEN SCHAEFER OR CONTRIBUTORS BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation
are those of the authors and should not be interpreted as representing
official policies, either expressed or implied, of Jorgen Schaefer.
"""

ABOUTHTML = """
<h1>%(APPLONGNAME)s v%(VERSIONSTRING)s</h1>
<b>%(COPYRIGHT)s</b><br />

<p>%(DESCRIPTION)s</p>

<p><a href="%(APPURL)s">Application Homepage</a></p>

<pre>%(LICENSE)s</pre>
""" % locals()
