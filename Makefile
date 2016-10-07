all: mig

mig: clean
	python manage.py makemigrations truco
	python manage.py migrate
	python manage.py shell < createusers

run:
	python manage.py runserver

sync:
	python manage.py syncdb

test:
	python manage.py test

test_models:
	python manage.py test truco.test.test_models

test_views:
	python manage.py test truco.test.test_views

test_integ:
	python manage.py test truco.test.test_integ

sh:
	python manage.py shell

clean:
	rm -f db.sqlite3 truco/migrations/*
	find . -name "*.pyc" -type f -delete
# lo de borrar los .pyc salio de aca:
# http://askubuntu.com/questions/377438/how-can-i-recursively-delete-all-files-of-a-specific-extension-in-the-current-di
