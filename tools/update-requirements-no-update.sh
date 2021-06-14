#!/bin/sh

pip-compile --no-emit-index-url requirements.in -o requirements.txt
pip-compile --no-emit-index-url requirements-test.in -o requirements-test.txt
pip-compile --no-emit-index-url requirements-dev.in -o requirements-dev.txt
