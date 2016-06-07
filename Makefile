.PHONY: install upgrade lint coverage travis docs

install:
	pip install -r requirements-dev.txt --process-dependency-links
	pip install -e . --process-dependency-links

upgrade:
	pip install -r requirements-dev.txt -U
	pip install -e . -U

lint:
	flake8

coverage:
	py.test --cov-report term-missing --cov erudit

spec:
	py.test --spec -p no:sugar

travis: install lint coverage
