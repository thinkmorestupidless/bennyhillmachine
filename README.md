# Benny Hill Machine

Guaranteed to make a video ~200% funnier.

## Running Locally

This is all Python, so make yourself a `<v|virtual>env` and then:

```shell script
pip install -r requirements.txt
```
> This project relies on `psycopg2` which will, in turn, require the `pg_config` executable.
> * Mac users - `brew install postgresql`
> * libpq-dev in Debian/Ubuntu
> * libpq-devel on Centos/Fedora/Cygwin/Babun

Now you have all the dependencies, you'll need 3 terminal windows:

1. For the web application
2. For the worker process
3. For the docker containers running the database and queue

### Start the docker containers

```shell script
cd dev
# initialises/runs Postgres database (and user) and Redis containers
docker compose up
```
> Postgres data is stored in `dev/.postgres` so if you need to nuke the database you can delete that directory and its contents and rebuild the containers with `rm -rf .postgres && docker compose up --build`

### Start the worker process

```shell script
python worker.py
```

### Start the web application

```shell script
flask run
```

Now you have everything running you can test by visiting http://localhost:5000 and pasting a YouTube url to the input text field.
