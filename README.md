# Install

It is recommended to use virtualenv:

    pyvenv toptool
    cd toptool
    . ./bin/activate

    git clone git@gitlab.fs.tum.de:biendarra/toptool.git

    pip install -r requirements.txt

# Dependencies

## Software

-   Python 3.5 or higher
-   pdflatex (from TeX Live)
-   txt2tags (to generate minutes)

## Python modules

See requirements.txt

# Run for development

Install requirements for development (e.g. pytest):

    pip install -r requirements_dev.txt

By default, Django uses a SQLite database that can be generated using the
following command inside the project directory:

    python manage.py migrate

Then a superuser should be created:

    python manage.py createsuperuser

Now you can start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

For testing simply run pytest:

    pytest

## Sample-Data/ "Fixtures"

you can generate example-data (overrides every model with data that looks partially plausible, but is clearly not
production-data)
by opening the django shell using:

```shell
python3 manage.py shell
```

In the shell type

```python
import toptool.fixtures

toptool.fixtures.showroom_fixture_state()
```

This operation might take a few seconds. Don't worry.

## Adding Depenencies

If you want to add a dependency that is in `pip` add it to the appropriate `requirements`-file.

# Translation

1. Update the `.po`-files with

```bash
python manage.py makemessages -a
```

2. Edit the `.po`-file. [Poedit](https://poedit.net) is an excellent GUI for this!

    In the Settings please change:

    |        Setting | to value |
    | -------------: | -------- |
    |           name | `$NAME`  |
    |          email | `$EMAIL` |
    |   Line endings | `Unix`   |
    |        Wrap at | `120`    |
    | check-spelling | `True`   |

3. Edit the `.po`-files, e.g. `guidedtours/locale/de/LC_MESSAGES/django.po`.

Note that `pre-commit` will automatically compile the translations for you.

# Staging

A staging environment is offered at `top.frank.elsinga.de`  
The username is `password`  
The password is `username`

## Building and running the dockerfile for local development

1. you need to save your environment variables in an `.env`-file.
   The further guide assumes content similar to the following in `staging/.env`.

```
DJANGO_DEBUG="True"
DJANGO_SECRET_KEY="CHOOSE_A_SAVE_PASSWORD"
DJANGO_ALLOWED_HOSTS="0.0.0.0,localhost,127.0.0.1"
```

2. Build the dockerfile

```
docker build -t toptool-staging:v1 .
```

3. Run the Dockerfile

```
docker run --env-file staging/.env -p 8080:8000 toptool-staging:v1
```

The Staging instance is now available at [`127.0.0.1:8080`](http://127.0.0.1:8080/) and is pushed to the GitHub Container Registry for convenience.
