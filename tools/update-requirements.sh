#!/bin/sh

pip-compile --no-emit-index-url -U requirements.in -o requirements.txt
