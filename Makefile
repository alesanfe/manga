install:
	pip install -r requirements.txt -r requirements-dev.txt

lint:
	isort .
	black .
	flake8

test:
	pytest

run:
	python manage.py runserver

docker-up:
	docker-compose -f docker/base/docker-compose.yml up -d --build

docker-down:
	docker-compose -f docker/base/docker-compose.yml down -v

docker-prod-up:
	# Prepare production env and start production compose
	docker-compose -f docker/prod/docker-compose.yml up -d --build

populate-db:
	docker-compose -f docker/base/docker-compose.yml run --rm populate-db

logs:
	docker-compose -f docker/base/docker-compose.yml logs -f

deploy:
	# Shortcut to deploy using production env
	docker-compose -f docker/prod/docker-compose.yml up -d --build

dev-up:
	# Start the dev compose (hot-reload) with local .env
	docker-compose -f docker/dev/docker-compose.yml up -d --build

dev-down:
	docker-compose -f docker/dev/docker-compose.yml down -v

db-setup:
	python manage.py makemigrations
	python manage.py migrate
	python manage.py flush --noinput
	python manage.py loaddata data/initial_data.json
	python manage.py shell -c "from utils.db_populate import populate_mangas; populate_mangas()"
	python manage.py shell -c "from utils.index_creator import index_all_mangas; index_all_mangas()"

