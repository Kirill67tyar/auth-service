migrate:
	poetry run python manage.py migrate contenttypes
	poetry run python manage.py migrate sessions
	poetry run python manage.py migrate admin
	poetry run python manage.py migrate auth_service

loaddata:
	poetry run python manage.py loaddata seed.json

runserver:
	poetry run python manage.py runserver
