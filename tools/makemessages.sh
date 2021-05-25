#!/bin/sh
python manage.py makemessages -e txt,py,html,xsl --no-wrap
python manage.py makemessages -d djangojs -i build -i build_dev --no-wrap
