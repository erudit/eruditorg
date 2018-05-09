NPM_ENV = tools/static/.env.json

.PHONY: all
all:
	@echo "make all doesn't do anything yet. run make assets"

node_modules:
	npm install

bower_components: node_modules
	npm run bower -- install

$(NPM_ENV): $(NPM_ENV).sample
	cp $^ $@

.PHONY: assets
assets: node_modules bower_components $(NPM_ENV)
	npm run gulp -- build --production
