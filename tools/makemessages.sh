#!/bin/sh
python manage.py makemessages -e txt,py,html,xsl
python manage.py makemessages -d djangojs -i build -i build_dev
