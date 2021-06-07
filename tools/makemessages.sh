#!/bin/sh
python manage.py makemessages -a -e txt,py,html,xsl --no-wrap
python manage.py makemessages -a -d djangojs -i build -i build_dev --no-wrap
