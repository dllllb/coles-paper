#!/usr/bin/env bash

mkdir data

wget https://storage.yandexcloud.net/di-datasets/data-science-bowl-2019.zip -O data-science-bowl-2019.zip
unzip -j data-science-bowl-2019.zip -d data
mv data-science-bowl-2019.zip data/
