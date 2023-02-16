.PHONY: build
build:
	docker buildx build --platform linux/arm64 -t localhost:2000/twitter --push .

lint:
	pre-commit run --all-files

mypy:
	mypy --package linkedin --namespace-packages

auth:
	store_keys && twitter-oauth
