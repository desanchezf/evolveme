#!/bin/sh

until python ./manage.py initsetup
do
  echo "Retrying initsetup command"
  sleep 5
done

python manage.py runserver 0.0.0.0:8000
