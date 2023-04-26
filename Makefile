.PHONY: build
build:
	sam build

.PHONY: deploy
deploy:
	sam deploy

.PHONY: release
release:
	sam build && sam deploy

.PHONY: local
local:
	sam local invoke -e sample_query.json

.PHONY: test
test:
	PYTHONPATH=src pytest
