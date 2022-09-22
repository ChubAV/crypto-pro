FROM ubuntu:latest

ENV TZ=Europe/Moscow
ENV LANG C.UTF-8
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DOCKER=true

RUN apt update &&  apt upgrade -y
RUN apt install cmake build-essential libboost-all-dev python3-dev python3-pip unzip vim apt-utils -y

RUN pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false

WORKDIR /dist

COPY linux-amd64_deb.tgz /dist/linux-amd64_deb.tgz
RUN tar xvf linux-amd64_deb.tgz
RUN linux-amd64_deb/install.sh
RUN apt install /dist/linux-amd64_deb/lsb-cprocsp-devel_*.deb

COPY cades-linux-amd64.tar.gz /dist/cades-linux-amd64.tar.gz
RUN tar xvf cades-linux-amd64.tar.gz
RUN apt install /dist/cprocsp-pki-cades*.deb

COPY pycades.zip /dist/pycades.zip
RUN unzip pycades.zip

RUN rm -r /dist/pycades_0.1.30636/CMakeLists.txt
COPY CMakeLists.txt /dist/pycades_0.1.30636/CMakeLists.txt

RUN mkdir /dist/pycades_0.1.30636/build
WORKDIR /dist/pycades_0.1.30636/build
RUN cmake ..
RUN make -j4
RUN cp pycades.so /usr/lib/python3.8/pycades.so

RUN     mkdir -p /app
WORKDIR /app/
COPY    pyproject_.toml /app/pyproject.toml
RUN     poetry install


RUN rm -r /dist
RUN rm -rf /var/lib/apt/lists/*


# CMD ["python3","loop.py"]



# build . --tag crypto-pro:latest --platform linux/amd64