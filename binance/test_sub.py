from utils.mqtt import Subscriber, Publisher

if __name__ == "__main__":

    broker = 'mosquitto'
    port = 1883
    topic = 'pair'
    client_id = 'machine1-sub'

    sub = Subscriber(broker, port, topic, client_id)
    sub.start_subscribe()
    