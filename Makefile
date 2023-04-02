.PHONY: install
install:
	python3 -m venv . \
		&& source ./bin/activate \
		&& pip3 install -r requirements.txt \
		&& deactivate


.PHONY: api
api:
	source ./bin/activate \
		&& python3 -m api


.PHONY: test
test:
	source ./bin/activate \
		&& python3 -m test
