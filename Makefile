build:
	docker-compose -f docker-compose.yml build

start-dev:
	docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans
