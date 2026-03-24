migrate:
	poetry run python manage.py migrate contenttypes
	poetry run python manage.py migrate sessions
	poetry run python manage.py migrate admin