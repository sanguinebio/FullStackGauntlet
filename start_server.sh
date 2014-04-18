#!/bin/bash
# Script to 

virtualenv --distribute ~/venv/phlebotomy
source ~/venv/phlebotomy/bin/activate

pip install django
python manage.py syncdb
python manage.py runserver

