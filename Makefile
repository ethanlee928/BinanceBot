build:
	docker-compose -f docker-compose.yml build

start-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

start-prod:
	docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans

ubuntu-build:
	docker compose -f docker-compose.yml build

ubuntu-dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d

ubuntu-prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

ubuntu-clean:
	docker compose -f docker-compose.yml down --remove-orphans
