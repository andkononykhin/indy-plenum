FROM hyperledger/indy-core-baseci:0.0.1
LABEL maintainer="Hyperledger <hyperledger-indy@lists.hyperledger.org>"

ARG uid=1000
ARG user=indy
ARG venv=venv

RUN echo "To invalidate cache"

RUN apt-get update -y && apt-get install -y \
    python3-nacl \
    libindy-crypto=0.4.1~46 \
    libindy=1.4.0~586 \
# rocksdb python wrapper
    libbz2-dev \
    zlib1g-dev \
    liblz4-dev \
    libsnappy-dev \
    rocksdb=5.8.8


RUN pip3 install -U pipenv

# TODO workaround (suggested by http://click.pocoo.org/5/python3/)
# to use pipenv's dependency 'click' (http://click.pocoo.org)
# check for alternatives
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

RUN indy_ci_add_user $uid $user $venv

RUN indy_image_clean

USER $user
WORKDIR /home/$user
