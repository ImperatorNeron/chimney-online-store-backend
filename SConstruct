import os

DC = "docker compose"
DL = "docker logs"
EXEC = "docker exec -it"

APP_FILE = "docker_compose/app.yaml"
APP_CONTAINER = "main-app"

STORAGES_FILE = "docker_compose/storages.yaml"
STORAGES_CONTAINER = "postgresql-container"

TEST_STORAGES_FILE = "docker_compose/test_storages.yaml"
TEST_STORAGES_CONTAINER = "postgresql-test-container"
TESTS = "pytest --cache-clear"

ENV = "--env-file .env"

ALREV = "alembic revision"
ALUP = "alembic upgrade"
ALDOWN = "alembic downgrade"


def app(target, source, env):
    command = f"{DC} -f {APP_FILE} -f {STORAGES_FILE} {ENV} up --build -d"
    # command = f"{DC} -f {APP_FILE} -f {STORAGES_FILE} -f {TEST_STORAGES_FILE} {ENV} up --build -d"
    return os.system(command)


def app_logs(target, source, env):
    command = f"{DL} {APP_CONTAINER} -f"
    return os.system(command)


def app_down(target, source, env):
    command = (
        f"{DC} -f {APP_FILE} -f {STORAGES_FILE} {ENV} down"
        # f"{DC} -f {APP_FILE} -f {STORAGES_FILE} -f {TEST_STORAGES_FILE} {ENV} down"
    )
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


# App with test db
Command("up", [], app)
Command("down", [], app_down)
Command("logs", [], app_logs)
Command("run-tests", [], run_tests)

# db
Command("auto-migrations", [], auto_migrations)
Command("migrate-up", [], migrate_up)
Command("migrate-down", [], migrate_down)
