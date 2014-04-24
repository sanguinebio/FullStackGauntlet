#!/bin/bash
# Script to 

virtualenv --distribute ~/venv/phlebotomy
source ~/venv/phlebotomy/bin/activate

pip install django
python manage_dev.py syncdb
python manage_dev.py runserver

