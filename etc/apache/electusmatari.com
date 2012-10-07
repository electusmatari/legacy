<VirtualHost *:80>
	ServerAdmin webmaster@electusmatari.com
	
	ServerName www.electusmatari.com
	ServerAlias electusmatari.com new.electusmatari.com
	
	ErrorLog /var/log/apache2/electusmatari.com-error.log

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog /var/log/apache2/electusmatari.com-access.log combined

	DocumentRoot /home/forcer/Projects/evecode/web/electusmatari.com/www

	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /home/forcer/Projects/evecode/web/electusmatari.com/www/>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		allow from all
	</Directory>

	#######################
	# Old em.com migration
	AcceptPathInfo on

	Alias /cvote/ /home/forcer/Projects/evecode/web/oldemcom/cvote/
	Alias /emapps/ /home/forcer/Projects/evecode/web/oldemcom/emapps/
	Alias /emapps.css /home/forcer/Projects/evecode/web/oldemcom/emapps.css

	<Directory /home/forcer/Projects/evecode/web/oldemcom/>
		Order deny,allow
		Allow from all
		Options +ExecCGI
		AddHandler cgi-script .cgi
	</Directory>

	RewriteEngine On
	RewriteRule ^/(oldadmin.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/(apps.*) /emapps/emapps.cgi/$1 [QSA,PT]
	Redirect /standings.cgi http://www.electusmatari.com/standings/
	RewriteRule ^/(standings.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/(market.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/gradient/deliveries.cgi /grd/deliveries.cgi [QSA,PT]
	RewriteRule ^/(gradient.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/(gallery.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/(forumtools.*) /emapps/emapps.cgi/$1 [QSA,PT]
	RewriteRule ^/vote(.*) /cvote/vote.cgi$1 [QSA,PT]

	#######################
	# LutiWiki
        RewriteRule ^/lutiwiki/(.*) /Programs/luti-wiki/index.php?title=$1 [QSA,L]
        Alias /luti-mediawiki /Programs/luti-wiki
        <Directory /Programs/luti-wiki/>
                Options +FollowSymLinks
                AllowOverride All
                order allow,deny
                allow from all
        </Directory>

        # some directories must be protected
        <Directory /Programs/luti-wiki/config>
                Options -FollowSymLinks
                AllowOverride None
        </Directory>
        <Directory /Programs/luti-wiki/upload>
                Options -FollowSymLinks
                AllowOverride None
        </Directory>

	#######################
	# MyBB
	Alias /forums /Programs/mybb/active/Upload
	<Directory /Programs/mybb/active/Upload/>
		Order deny,allow
		Allow from all
	</Directory>

	#######################
	# EDK
	Alias /killboard/ /Programs/edk/active/
	<Directory /Programs/edk/active/>
		Order deny,allow
		Allow from all
	</Directory>

	#######################
	# MediaWiki
	RewriteRule ^/wiki/(.*) /var/lib/mediawiki/index.php?title=$1 [QSA,L]
	Alias /mediawiki /var/lib/mediawiki
	<Directory /var/lib/mediawiki/>
	        Options +FollowSymLinks
        	AllowOverride All
	        order allow,deny
        	allow from all
	</Directory>

	# some directories must be protected
	<Directory /var/lib/mediawiki/config>
	        Options -FollowSymLinks
	        AllowOverride None
	</Directory>
	<Directory /var/lib/mediawiki/upload>
	        Options -FollowSymLinks
	        AllowOverride None
	</Directory>

	#######################
        # Upgrades
        RedirectMatch ^/gmi(.*)$ http://gradient.electusmatari.com/index$1

	#######################
	# Django
	Alias /media/admin/ /usr/share/pyshared/django/contrib/admin/media/
	<Directory /usr/share/pyshared/django/contrib/admin/media/>
		Order deny,allow
		Allow from all
	</Directory>

	Alias /download/ /home/forcer/www/electusmatari.com/download/
	Alias /favicon.ico /home/forcer/Projects/evecode/web/electusmatari.com/www/favicon.ico
	Alias /media/ /home/forcer/Projects/evecode/web/electusmatari.com/www/media/

	<Directory /home/forcer/Projects/evecode/web/electusmatari.com/www/>
		Order deny,allow
		Allow from all
	</Directory>

	RedirectMatch ^/$ http://www.electusmatari.com/forums/
	
	WSGIScriptAlias / /home/forcer/Projects/evecode/web/electusmatari.com/data/python/emtools/wsgi/emtools.wsgi

	<Directory /home/forcer/Projects/evecode/web/electusmatari.com/data/python/emtools/wsgi/>
		Order deny,allow
		Allow from all
	</Directory>

	<Directory /Programs/awstats/www/>
        	Options +ExecCGI +FollowSymLinks
	        AllowOverride AuthConfig
		DirectoryIndex awstats.cgi
		AddHandler cgi-script .cgi
	</Directory>

	Alias /awstats-icon/ /usr/share/awstats/icon/
	Alias /awstats/ /Programs/awstats/www/
</VirtualHost>
