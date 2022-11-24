FROM python:3.11

RUN apt-get update
RUN pip3 install --upgrade pip && \
    pip3 install numpy python-binance paho-mqtt matplotlib mplfinance pandas overrides

RUN apt-get install -y --no-install-recommends tzdata
RUN TZ=Asia/Hong_Kong \
    && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && dpkg-reconfigure -f noninteractive tzdata 
