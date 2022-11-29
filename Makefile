mode?=
ifdef mode
	mode:=${mode}
endif
export MODE=${mode}

release_version?=

build:
	docker-compose -f docker-compose.yml build

start:
	docker-compose -f docker-compose.yml -f docker-compose.${mode}.yml up -d

clean:
	docker-compose -f docker-compose.yml down --remove-orphans

release:
	docker build ./ -f ./binance/Dockerfile.prod -t binancebot:${release_version} && \
	docker build ./ -f ./slack/Dockerfile.prod -t slackbot:${release_version}
