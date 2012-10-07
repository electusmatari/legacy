<VirtualHost *:80>
	ServerAdmin arkady@arkady-sadik.de
	
	ServerName gradient.electusmatari.com
	
	ErrorLog /var/log/apache2/gradient.electusmatari.com-error.log

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog /var/log/apache2/gradient.electusmatari.com-access.log combined

	DocumentRoot /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/

	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		allow from all
	</Directory>

        RedirectMatch /gmi(.*)$ http://gradient.electusmatari.com/index$1

        #######################
        # Wiki
	RewriteEngine on
        RewriteRule ^/wiki/(.*) /Programs/grd-wiki/index.php?title=$1 [QSA,L]
        Alias /mediawiki /Programs/grd-wiki
        <Directory /Programs/grd-wiki/>
                Options +FollowSymLinks
                AllowOverride All
                order allow,deny
                allow from all
        </Directory>

        # some directories must be protected
        <Directory /Programs/grd-wiki/config>
                Options +FollowSymLinks
                AllowOverride None
        </Directory>
        <Directory /Programs/grd-wiki/upload>
                Options -FollowSymLinks
                AllowOverride None
        </Directory>

	#######################
	# Django
	Alias /media/admin/ /usr/share/pyshared/django/contrib/admin/media/
	<Directory /usr/share/pyshared/django/contrib/admin/media/>
		Order deny,allow
		Allow from all
	</Directory>

	Alias /robots.txt /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/robots.txt
	Alias /favicon.ico /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/favicon.ico
	Alias /media/ /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/media/

	<Directory /home/forcer/Projects/evecode/web/gradient.electusmatari.com/www/>
		Order deny,allow
		Allow from all
	</Directory>
	
	WSGIScriptAlias / /home/forcer/Projects/evecode/web/gradient.electusmatari.com/data/python/gradient/wsgi/gradient.wsgi
	<Directory /home/forcer/Projects/evecode/web/gradient.electusmatari.com/data/python/gradient/>
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>
