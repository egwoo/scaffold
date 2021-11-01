.DEFAULT_GOAL := charts

-include $(shell while [ $PWD != "/" ]; do test -e infra/build-harness && { pwd; break; }; cd .. ; done)/infra/build-harness/harness.mk

.PHONY: build
build: docker/default submake/default

.PHONY: charts
charts: build helm/default
