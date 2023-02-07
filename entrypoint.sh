#!/usr/bin/env sh

gunicorn wsgi:app --bind 0.0.0.0:5000 --reload -w 4