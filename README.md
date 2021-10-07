# Install

It is recommended to use virtualenv:

    pyvenv toptool
    cd toptool
    . ./bin/activate

    git clone git@gitlab.fs.tum.de:biendarra/toptool.git

    pip install -r requirements.txt

# Dependencies

## Software

 * Python 3.5 or higher
 * pdflatex (from TeX Live)
 * txt2tags (to generate minutes)

## Python modules

See requirements.txt

# Run for development

Install requirements for development (e.g. pytest):

    pip install -r requirements_dev.txt

By default Django uses a SQLite database that can be generated using the
following command inside the project directory:

    python manage.py migrate

Then a superuser should be created:

    python manage.py createsuperuser

Now you can start the webserver for development:

    python manage.py runserver

Now visit http://localhost:8000 with your browser.

For testing simply run pytest:

    pytest

# Translation

Update the .po files with:

    python manage.py makemessages -l en

Then edit the .po files, e.g. locale/en/LC_MESSAGES/django.po.
poedit is an excellent GUI for this!

Finally create the .mo files with the new translations:

    python manage.py compilemessages
