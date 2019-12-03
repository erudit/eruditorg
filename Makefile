PYTHON ?= python3
REQ_PYTHON_MINOR_VERSION = 4
ENV = env
NPM_ENV = tools/static/.env.json

.PHONY: all
all: $(ENV)/updated

reqs:
	@ret=`${PYTHON} -c "import sys; print(int(sys.version_info[:2] >= (3, ${REQ_PYTHON_MINOR_VERSION})))"`; \
		if [ $${ret} -ne 1 ]; then \
			echo "Python 3.${REQ_PYTHON_MINOR_VERSION}+ required. Aborting."; \
			exit 1; \
		fi
		@${PYTHON} -m venv -h > /dev/null || \
	echo "Creation of our virtualenv failed. You probably need python3-venv."

$(ENV): | reqs
	@echo "Creating our virtualenv"
	${PYTHON} -m venv $(ENV)

$(ENV)/updated: $(ENV) requirements-dev.txt requirements.txt
	$(ENV)/bin/python -m pip install -U -r requirements-dev.txt
	touch $@

node_modules:
	npm install

$(NPM_ENV): $(NPM_ENV).sample
	cp $^ $@

.PHONY: assets
assets: node_modules $(NPM_ENV)
	npm run gulp -- build --production
