include .env
export

PORT := 8080
ECR_REPOSITORY := $(AWS_ACCOUNT_ID).dkr.ecr.ap-northeast-1.amazonaws.com
SHORT_SHA := $(shell git rev-parse --short HEAD)
DOCKER_TAG := latest
DOCKER_PREDICTOR_IMAGE := $(USER_NAME)-mlops-practice/predictor
DOCKER_PREDICTOR_CANARY_IMAGE := $(USER_NAME)-mlops-practice/predictor-canary
DOCKER_ML_IMAGE := $(USER_NAME)-mlops-practice/ml-pipeline
DOCKER_GRAFANA_IMAGE := $(USER_NAME)-mlops-practice/grafana
DOCKER_PROMETHEUS_IMAGE := $(USER_NAME)-mlops-practice/prometheus
DOCKER_PUSHGATEWAY_IMAGE := $(USER_NAME)-mlops-practice/pushgateway
DOCKER_FLUENTD_IMAGE := $(USER_NAME)-mlops-practice/fluentd
DOCKER_IMPORTER_IMAGE := $(USER_NAME)-mlops-practice/importer
DOCKER_ECS_EXPORTER_IMAGE := $(USER_NAME)-mlops-practice/ecs-exporter
DOCKERFILE_REPOSITORY := docker
DOCKERFILE_ML := Dockerfile
DOCKERFILE_GRAFANA := Dockerfile.grafana
DOCKERFILE_PROMETHEUS := Dockerfile.prometheus
DOCKERFILE_PUSHGATEWAY := Dockerfile.pushgateway
DOCKERFILE_FLUENTD := Dockerfile.fluentd
DOCKERFILE_IMPORTER := Dockerfile.importer


.PHONY: update-lib
update-lib:
	poetry lock
	poetry install --sync --no-root
	poetry run task update_dev
	poetry run task update_ml
	poetry run task update_predictor
	poetry run task update_importer


.PHONY: format
format:
	poetry run ruff format .
	poetry run ruff check . --fix
	poetry run mypy . --no-site-packages
	terraform fmt --recursive


.PHONY: build-ml
build-ml:
	docker build --platform=linux/amd64 --build-arg NAME=$(USER_NAME) --target ml -t $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_ML) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):$(DOCKER_TAG)


.PHONY: push-ml
push-ml:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):$(DOCKER_TAG)


.PHONY: run-ml
run-ml:
	docker build --build-arg NAME=$(USER_NAME) --target ml -t $(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE):latest -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_ML) .
	docker run --rm -it -v $(HOME)/.aws/credentials:/root/.aws/credentials:ro \
				-e AWS_PROFILE=$(AWS_PROFILE) \
				-e MODEL=sgd_classifier_ctr_model \
				-e SYSTEM_ENV=local \
				--network mlops-practice \
				$(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE)
	docker run --rm -it -v $(HOME)/.aws/credentials:/root/.aws/credentials:ro \
				-e AWS_PROFILE=$(AWS_PROFILE) \
				-e MODEL=sgd_classifier_ctr_optuna_model \
				-e SYSTEM_ENV=local \
				--network mlops-practice \
				$(ECR_REPOSITORY)/$(DOCKER_ML_IMAGE)


.PHONY: build-predictor
build-predictor:
	docker build --platform=linux/amd64 --build-arg NAME=$(USER_NAME) --target predictor -t $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_ML) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_IMAGE):$(DOCKER_TAG)


.PHONY: push-predictor
push-predictor:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_IMAGE):$(DOCKER_TAG)


.PHONY: build-grafana
build-grafana:
	docker build --platform=linux/amd64 -t $(ECR_REPOSITORY)/$(DOCKER_GRAFANA_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_GRAFANA) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_GRAFANA_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_GRAFANA_IMAGE):$(DOCKER_TAG)

.PHONY: push-grafana
push-grafana:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_GRAFANA_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_GRAFANA_IMAGE):$(DOCKER_TAG)


.PHONY: build-prometheus
build-prometheus:
	docker build --platform=linux/amd64 -t $(ECR_REPOSITORY)/$(DOCKER_PROMETHEUS_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_PROMETHEUS) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_PROMETHEUS_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_PROMETHEUS_IMAGE):$(DOCKER_TAG)


.PHONY: push-prometheus
push-prometheus:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_PROMETHEUS_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_PROMETHEUS_IMAGE):$(DOCKER_TAG)


.PHONY: build-pushgateway
build-pushgateway:
	docker build --platform=linux/amd64 -t $(ECR_REPOSITORY)/$(DOCKER_PUSHGATEWAY_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_PUSHGATEWAY) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_PUSHGATEWAY_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_PUSHGATEWAY_IMAGE):$(DOCKER_TAG)


.PHONY: push-pushgateway
push-pushgateway:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_PUSHGATEWAY_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_PUSHGATEWAY_IMAGE):$(DOCKER_TAG)


.PHONY: build-predictor-canary
build-predictor-canary:
	docker build --platform=linux/amd64 --build-arg NAME=$(USER_NAME) --target predictor-canary -t $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_CANARY_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_ML) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_CANARY_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_CANARY_IMAGE):$(DOCKER_TAG)


.PHONY: push-predictor-canary
push-predictor-canary:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_CANARY_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_PREDICTOR_CANARY_IMAGE):$(DOCKER_TAG)


.PHONY: build-fluentd
build-fluentd:
	docker build --platform=linux/amd64 -t $(ECR_REPOSITORY)/$(DOCKER_FLUENTD_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_FLUENTD) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_FLUENTD_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_FLUENTD_IMAGE):$(DOCKER_TAG)


.PHONY: push-fluentd
push-fluentd:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_FLUENTD_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_FLUENTD_IMAGE):$(DOCKER_TAG)

.PHONY: build-importer
build-importer:
	docker build --platform=linux/amd64 -t $(ECR_REPOSITORY)/$(DOCKER_IMPORTER_IMAGE):$(SHORT_SHA) -f $(DOCKERFILE_REPOSITORY)/$(DOCKERFILE_IMPORTER) .
	docker tag $(ECR_REPOSITORY)/$(DOCKER_IMPORTER_IMAGE):$(SHORT_SHA) $(ECR_REPOSITORY)/$(DOCKER_IMPORTER_IMAGE):$(DOCKER_TAG)

.PHONY: push-importer
push-importer:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_IMPORTER_IMAGE):$(SHORT_SHA) && docker push $(ECR_REPOSITORY)/$(DOCKER_IMPORTER_IMAGE):$(DOCKER_TAG)

.PHONY: build-ecs-exporter
build-ecs-exporter:
	docker pull --platform=linux/amd64 prometheuscommunity/ecs-exporter:latest
	docker tag prometheuscommunity/ecs-exporter:latest $(ECR_REPOSITORY)/$(DOCKER_ECS_EXPORTER_IMAGE):latest
	docker tag prometheuscommunity/ecs-exporter:latest $(ECR_REPOSITORY)/$(DOCKER_ECS_EXPORTER_IMAGE):$(SHORT_SHA)

.PHONY: push-ecs-exporter
push-ecs-exporter:
	aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $(ECR_REPOSITORY)
	docker push $(ECR_REPOSITORY)/$(DOCKER_ECS_EXPORTER_IMAGE):latest && docker push $(ECR_REPOSITORY)/$(DOCKER_ECS_EXPORTER_IMAGE):$(SHORT_SHA)

.PHONY: build
build: build-ml build-predictor build-grafana build-prometheus build-predictor-canary build-pushgateway build-fluentd build-importer build-ecs-exporter


.PHONY: push
push: push-ml push-predictor push-grafana push-prometheus push-predictor-canary push-pushgateway push-fluentd push-importer push-ecs-exporter


.PHONY: init
init:
	terraform -chdir=infra init


.PHONY: plan
plan:
	terraform -chdir=infra plan


.PHONY: apply
apply:
	terraform -chdir=infra apply


.PHONY: destroy
destroy:
	terraform -chdir=infra destroy


.PHONY: upload
upload:
	aws s3 cp data/train.tsv s3://$(S3_BUCKET)/train_data/train.tsv
	aws s3 cp data/click.tsv.gz s3://$(S3_BUCKET)/train_data/click.tsv.gz


.PHONY: predict
predict:
	while read line; do \
		curl -X 'POST' 'http://localhost:$(PORT)/predict' \
			-H 'accept: application/json' \
			-H 'Content-Type: application/json' \
			-d "$$line"; \
		echo; \
		sleep 1; \
	done < ./data/sample.jsonl


.PHONY: predict-ecs
predict-ecs:
	while read line; do \
		curl -X 'POST' '$(AWS_ALB_DNS)/predict' \
			-H 'accept: application/json' \
			-H 'Content-Type: application/json' \
			-d "$$line"; \
		echo; \
		sleep 1; \
	done < ./data/sample.jsonl
