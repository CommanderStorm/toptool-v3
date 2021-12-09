from subprocess import run  # nosec: used for flushing the db

import django.utils.timezone
from django.contrib.auth import get_user_model
from django.utils.datetime_safe import datetime


def showroom_fixture_state():
    confirmation = input(
        "Do you really want to load the showroom fixture? (This will flush the database) [y/n]",
    )
    if confirmation.lower() != "y":
        return
    showroom_fixture_state_no_confirmation()


def showroom_fixture_state_no_confirmation():  # nosec: this is only used in a fixture
    run(["python3", "manage.py", "flush", "--noinput"], check=True)

    # user
    _generate_superuser_frank()


def _generate_superuser_frank():  # nosec: this is only used in a fixture
    return get_user_model().objects.create(
        username="frank",
        password="pbkdf2_sha256$216000$DHqZuXE7LQwJ$i8iIEB3qQN+NXMUTuRxKKFgYYC5XqlOYdSz/0om1FmE=",
        first_name="Frank",
        last_name="Elsinga",
        is_superuser=True,
        is_staff=True,
        is_active=True,
        email="elsinga@fs.tum.de",
        date_joined=django.utils.timezone.make_aware(datetime.today()),
    )
