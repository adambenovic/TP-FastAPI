# FastAPI

TP Team 11 FastAPI Backend

### Run instructions DEV LOCAL

```./run_local.sh```

or alternatively

```make up```

### Run instructions HOSTED

Run ```docker-compose up -d``` from `hosted` directory



### Usage
You can find:
- Postgre on port 5433
- API on port 8081
- Adminer on port 8082
- PgAdmin on port 8083

### Migrations

Migrations rely on [Alembic](https://alembic.sqlalchemy.org/en/latest/tutorial.html).
Use the [installation](https://alembic.sqlalchemy.org/en/latest/front.html#installation) page to
setup local venv for generating and running migrations.

To generate migration from current code use command:
```shell
alembic revision --autogenerate -m "migration name"
```
or
```shell
make migrations-d m="update-name"
```

To migrate to newest version, run command:

```shell
alembic upgrade head
```
or
```shell
make migrations-m
```
