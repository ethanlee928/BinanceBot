# BinanceBot

A simple bot ultilising Binance API, Slack API, and MQTT to monitor the crypto market.


## Prerequisite

- prepare .env file in the root directory
```bash
BINANCE_KEY={YOUR BINANCE KEY}
BINANCE_SECRET={YOUR BINANCE SECRET}
SLACK_EVENT_TOKEN= {YOUR SIGNING SECRET}
SLACK_TOKEN={Bot User OAuth Token}
```

- Enable Event Subscription:
    - First create new app 
    - Click on Event Subscription -> Enable Events
    - Input Request URL: http://{hostname}:5001/slack/events (It will be verified only after the slackbot server is started)


## Get Started

```
# How to start all services
make build

# Start development mode
make mode=dev start

# Start production mode
make mode=prod start
```
