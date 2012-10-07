APPNAME = "GDU"
APPLONGNAME = "Gradient Data Uploader"
APPURL = "http://gradient.electusmatari.com/uploader/"
AUTH_TOKEN_URL = "http://gradient.electusmatari.com/uploader/token/"

VENDORNAME = "Gradient"
COPYRIGHT = "Copyright (C) 2011, 2012 Jorgen Schaefer"

VERSION = 1.1
VERSIONSTRING = "%.1f" % VERSION

DESCRIPTION = """\
The Gradient Data Uploader is a data mining tool that watches the
cache files of EVE Online clients for interesting data, extracts the
data, and uploads it to the Gradient website.\
"""

ABOUT = """\
%s v%s
Copyright (c) 2011, 2012 Jorgen Schaefer. All rights reserved.
(aka Arkady Sadik)
""" % (APPLONGNAME, VERSIONSTRING)

LICENSE = """\
Copyright 2011, 212 Jorgen Schaefer. All rights reserved.

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

REVERENCE_LICENSE = """\
Copyright (c) 2003-2009 Jamie "Entity" van den Berge
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * The name of the author may not be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY Jamie van den Berge ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL Jamie van den Berge BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

It is the responsibility of all users of this code and developers of derived
works to ensure that their use and activities comply with all laws as well as
the EVE-Online End-User License Agreement and Terms of Service.
"""

ABOUTHTML = """
<h1>%(APPLONGNAME)s v%(VERSIONSTRING)s</h1>
<b>%(COPYRIGHT)s</b><br />

<p>%(DESCRIPTION)s</p>

<p><a href="%(APPURL)s">Application Homepage</a></p>

<h2>%(APPLONGNAME)s License</h2>

<pre>%(LICENSE)s</pre>

<h2>Additional Licenses</h2>

<h3>Python&#174;</h3>

<p>The Gradient Data Uploader is written using the <a
href="http://www.python.org/">Python</a> language. "Python" is a
registered trademark of the Python Software Foundation.</p>

<h3>WxWidgets</h3>

<p>The uploader is using the <a
href="http://www.wxwidgets.org/">WxWidgets</a> widget library.</p>

<h3>Reverence</h3>

<p>To read the EVE client cache, we use the <a
href="https://github.com/ntt/reverence/">Reverence</a> cache reading
library.</p>

<p>Copyright (c) 2003-2009 Jamie "Entity" van den Berge<br />
All rights reserved.</p>

<p>Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:</p>

<ul>
  <li>Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.</li>
  <li>Redistributions in binary form must reproduce the above
      copyright notice, this list of conditions and the following
      disclaimer in the documentation and/or other materials provided
      with the distribution.</li>
  <li>The name of the author may not be used to endorse or promote
      products derived from this software without specific prior
      written permission.</li>
</ul>

<p>THIS SOFTWARE IS PROVIDED BY Jamie van den Berge ''AS IS'' AND ANY
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL Jamie van den Berge BE
LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.</p>

<p>It is the responsibility of all users of this code and developers
of derived works to ensure that their use and activities comply with
all laws as well as the EVE-Online End-User License Agreement and
Terms of Service.</p>

<h3>Python for Windows extensions</h3>

<p>To keep track of changes in the cache directory, we use the <a
href="http://sourceforge.net/projects/pywin32/">PyWin32</a>
library.</p>

<h3>EVE Online</h3>

<p>This whole uploader would not make sense or be useful without the
great game of <a href="http://www.eveonline.com/">EVE Online</a> by <a
href="http://www.ccpgames.com/">CCP Games hf</a>.</p>

<p>All Eve Related Materials are Property Of CCP Games EVE-related
data and information is used with limited permission of CCP Games hf.
No official affiliation or endorsement by CCP Games hf is stated or
implied.</p>

<p>EVE Online and the EVE logo are the registered trademarks of CCP
hf. All rights are reserved worldwide. All other trademarks are the
property of their respective owners. EVE Online, the EVE logo, EVE and
all associated logos and designs are the intellectual property of CCP
hf. All artwork, screenshots, characters, vehicles, storylines, world
facts or other recognizable features of the intellectual property
relating to these trademarks are likewise the intellectual property of
CCP hf. CCP hf. has granted permission to the Gradient Data Uploader
to use EVE Online and all associated logos and designs for promotional
and information purposes on its website but does not endorse, and is
not in any way affiliated with, Gradient Data Uploader. CCP is in
no way responsible for the content on or functioning of this program,
nor can it be liable for any damage arising from the use of this
program.</p>
""" % locals()
