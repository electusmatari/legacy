<VirtualHost *:80>
	ServerAdmin arkady@arkady-sadik.de
	
	ServerName api.electusmatari.com
	
	ErrorLog /var/log/apache2/api.electusmatari.com-error.log

	# Possible values include: debug, info, notice, warn, error, crit,
	# alert, emerg.
	LogLevel warn

	CustomLog /var/log/apache2/api.electusmatari.com-access.log combined

	DocumentRoot /home/forcer/Projects/evecode/web/api.electusmatari.com/www/

	<Directory />
		Options FollowSymLinks
		AllowOverride None
	</Directory>
	<Directory /home/forcer/Projects/evecode/web/api.electusmatari.com/www/>
		Options Indexes FollowSymLinks MultiViews
		AllowOverride None
		Order allow,deny
		allow from all
	</Directory>

	#######################
	# Django
	# Alias /media/admin/ /usr/share/pyshared/django/contrib/admin/media/
	# <Directory /usr/share/pyshared/django/contrib/admin/media/>
	# 	Order deny,allow
	#	Allow from all
	# </Directory>

	WSGIScriptAlias / /home/forcer/Projects/evecode/web/api.electusmatari.com/data/python/apiemcom/wsgi/api.wsgi
	<Directory /home/forcer/Projects/evecode/web/api.electusmatari.com/data/python/apiemcom/wsgi/>
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>
