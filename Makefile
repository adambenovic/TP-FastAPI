# Executables (local)
DOCKER_COMP = docker-compose -f docker-compose-dev.yml

# Docker containers
FASTAPI_CONT = $(DOCKER_COMP) exec fastapi

# Executables
ALEMBIC  = $(FASTAPI_CONT) alembic

# Misc
.DEFAULT_GOAL = help
.PHONY        = help build up start down logs sh

help: ## Outputs this help screen
	@grep -E '(^[a-zA-Z0-9_-]+:.*?##.*$$)|(^##)' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}{printf "\033[32m%-30s\033[0m %s\n", $$1, $$2}' | sed -e 's/\[32m##/[33m/'

build: ## Builds the Docker images
	@$(DOCKER_COMP) build --pull --no-cache

up: ## Start the docker hub in detached mode (no logs)
	@$(DOCKER_COMP) up --detach

down: ## Stop the docker hub
	@$(DOCKER_COMP) down --remove-orphans

logs: ## Show live logs
	@$(DOCKER_COMP) logs --tail=0 --follow

sh: ## Connect to the fastapi container
	@$(FASTAPI_CONT) sh

alembic: ## pass the parameter "c=" to run a given command, example: make alembic c='upgrade head'
	@$(eval c ?=)
	@$(ALEMBIC) $(c)

migrations-d: ## Generate diff migration, pass the parameter "m='migration'" for message
	@$(eval m ?=)
	@$(ALEMBIC) revision --autogenerate -m $(m)

migrations-m: ## Migrate to latest migration version
	@$(ALEMBIC) upgrade head
