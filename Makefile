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

js/bower_packed.js css/bower_packed.css: bower_components/**/* bin/pack-bower
	bin/pack-bower

css: css/theme.min.css

css/theme.min.css: css/theme.styl
	yarn run stylus -c -m css/theme.styl -o css/theme.min.css

js: js/ui.min.js

js/ui.min.js: js/ui.js
	yarn run babel js/ui.js -s -o js/ui.min.js
