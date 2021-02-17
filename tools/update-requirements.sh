#!/bin/sh

pip-compile --no-emit-index-url -U requirements.in -o requirements.txt
pip-compile --no-emit-index-url -U requirements-test.in -o requirements-test.txt
pip-compile --no-emit-index-url -U requirements-dev.in -o requirements-dev.txt
