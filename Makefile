.PHONY: default prereqs site assets bower css js

default: site

prereqs:
	pip install -r requirements.txt
	yarn install

site: assets
	bin/generate -p configs/config.yml

site-local: assets
	bin/generate -p configs/config-local.yml

assets: bower css js

bower: js/bower_packed.js css/bower_packed.css

js/bower_packed.js css/bower_packed.css: bower_components/**/*
	bin/pack-bower

css: css/theme.css

css/theme.css: css/theme.styl
	yarn run stylus -- -m css/theme.styl -o css/theme.css

js: js/ui.js
