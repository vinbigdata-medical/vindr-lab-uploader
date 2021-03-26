TAG := vindr/vinlab-dicom-uploader:latest

.PHONY: tests

tests:
	docker build -t test .
	#docker run --entrypoint test

build:
	docker build -t ${TAG} .
