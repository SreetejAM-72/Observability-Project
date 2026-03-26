#!/usr/bin/env bash
set -euo pipefail

rm -rf build
mkdir -p build

pip install -r lambda/requirements.txt -t build

cp lambda/*.py build/

cd build
zip -r lambda.zip .