mode?=
ifdef mode
	mode:=${mode}
endif
export MODE=${mode}

build:
	docker-compose -f docker-compose.yml build

start:
	docker-compose -f docker-compose.yml -f docker-compose.${mode}.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans

ubuntu-build:
	docker compose -f docker-compose.yml build

ubuntu-start:
	docker compose -f docker-compose.yml -f docker-compose.${mode}.yml up -d

ubuntu-clean:
	docker compose -f docker-compose.yml down --remove-orphans
