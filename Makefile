.PHONY: install
install:
	python3 -m venv . \
		&& source ./bin/activate \
		&& pip3 install -r requirements.txt \
		&& deactivate


.PHONY: itinerary_gen_api
itinerary_gen_api:
	source ./bin/activate \
		&& python3 -m itinerary_gen_api


.PHONY: recommender_api
recommender_api:
	source ./bin/activate \
		&& python3 -m recommender_api


.PHONY: test
test:
	source ./bin/activate \
		&& python3 -m test
