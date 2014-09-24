ENV=virtualenv
WHEELSDIR=./wheels

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


.PHONY: test build pip-wheel build-wheels clean install-debs upload
.DEFAULT_GOAL := test
