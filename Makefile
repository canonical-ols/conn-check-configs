ENV=virtualenv
WHEELSDIR=./wheels
CONN_CHECK_CONFIGS_VERSION=$(shell cat conn_check_configs/version.txt)
CONN_CHECK_PPA=ppa:wesmason/conn-check

$(ENV):
	virtualenv $(ENV)

build: $(ENV)
	$(ENV)/bin/pip install nose pyyaml
	$(ENV)/bin/python setup.py develop

test: $(ENV)
	$(ENV)/bin/nosetests

clean-wheels:
	-rm -r $(WHEELSDIR)

clean: clean-wheels
	-rm -r $(ENV)
	find . -name "*.pyc" -delete

install-debs:
	sudo xargs --arg-file deb-dependencies.txt apt-get install -y

install-deb-pkg-debs: install-debs
	sudo apt-get install -y build-essential packaging-dev dh-make

pip-wheel: $(ENV)
	@$(ENV)/bin/pip install wheel

$(WHEELSDIR):
	mkdir $(WHEELSDIR)

build-wheels: pip-wheel $(WHEELSDIR) $(ENV)
	$(ENV)/bin/pip wheel --wheel-dir=$(WHEELSDIR) .

upload: test pip-wheel
	$(ENV)/bin/python setup.py sdist bdist_wheel upload
	@echo
	@echo "Don't forget: bzr tag" `cat conn_check_configs/version.txt` '&& bzr push'

build-deb: $(ENV)
	-rm ../python-conn-check_*-*
	-rm ../conn-check-configs_*-*
	-ls ../conn-check-configs_*.orig.tar.gz | grep -v '.*$(CONN_CHECK_CONFIGS_VERSION).*' | xargs rm
	$(ENV)/bin/python setup.py sdist
	cp dist/conn-check-configs-$(CONN_CHECK_CONFIGS_VERSION).tar.gz ../conn-check-configs_$(CONN_CHECK_CONFIGS_VERSION).orig.tar.gz
	debuild -S -sa

test-build-deb: build-deb
	debuild

update-ppa:
	cd .. && dput $(CONN_CHECK_PPA) conn-check-configs_$(CONN_CHECK_CONFIGS_VERSION)-*_source.changes


.PHONY: test build pip-wheel build-wheels clean install-debs upload
.DEFAULT_GOAL := test
