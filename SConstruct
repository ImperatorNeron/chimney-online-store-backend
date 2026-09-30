import os

DC = "docker compose"
DL = "docker logs"
EXEC = "docker exec -it"

APP_CONTAINER = "main-app"

STORAGES_FILE = "docker_compose/storages.yaml"
STORAGES_CONTAINER = "postgresql-container"

APP_DEV_FILE = "docker_compose/app.dev.yaml"
APP_PROD_FILE = "docker_compose/app.prod.yaml"

TEST_STORAGES_FILE = "docker_compose/test_storages.yaml"
TEST_STORAGES_CONTAINER = "postgresql-test-container"
TESTS = "pytest --cache-clear"

ENV = "--env-file .env"

ALREV = "alembic revision"
ALUP = "alembic upgrade"
ALDOWN = "alembic downgrade"


def app_dev(target, source, env):
    command = f"{DC} -f {APP_DEV_FILE} -f {STORAGES_FILE} {ENV} up --build -d"
    return os.system(command)


def app_prod(target, source, env):
    command = f"{DC} -f {APP_PROD_FILE} -f {STORAGES_FILE} {ENV} up --build -d"
    return os.system(command)


def app_dev_down(target, source, env):
    command = f"{DC} -f {APP_DEV_FILE} -f {STORAGES_FILE} {ENV} down"
    return os.system(command)


def app_prod_down(target, source, env):
    command = f"{DC} -f {APP_PROD_FILE} -f {STORAGES_FILE} {ENV} down"
    return os.system(command)


def app_logs(target, source, env):
    command = f"{DL} {APP_CONTAINER} -f"
    return os.system(command)


def run_tests(target, source, env):
    command = f"{EXEC} {APP_CONTAINER} {TESTS}"
    return os.system(command)


def auto_migrations(target, source, env):
    command = f"{EXEC} {APP_CONTAINER} {ALREV} --autogenerate -m 'dts'"
    return os.system(command)


def migrate_up(target, source, env):
    command = f"{EXEC} {APP_CONTAINER} {ALUP} head"
    return os.system(command)


def migrate_down(target, source, env):
    command = f"{EXEC} {APP_CONTAINER} {ALDOWN} base"
    return os.system(command)


Command("devup", [], app_dev)
Command("produp", [], app_prod)
Command("devdown", [], app_dev_down)
Command("proddown", [], app_prod_down)
Command("logs", [], app_logs)
Command("run-tests", [], run_tests)

# db
Command("auto-migrations", [], auto_migrations)
Command("migrate-up", [], migrate_up)
Command("migrate-down", [], migrate_down)
