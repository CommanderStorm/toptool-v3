import random
from datetime import timedelta
from subprocess import run  # nosec: used for flushing the db

import django.utils.timezone
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
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
    _generate_superusers()


def rand_company_name():
    cool_names = ["Caliburst", "Ironhide", "Stylor", "Spectro", "Camshaft", "Haywire", "Snarl", "Starscream"]
    violent_names = ["Warpath", "Recoil", "Broadside", "Scattershot", "Thundercracker"]
    lame_names = ["Scrapper", "Streetwise", "Arcana", "Grax", "Drag Strip", "Chromedome", "Slag"]
    return random.choice(cool_names + violent_names + lame_names)


def rand_firstname():
    male_names = ["Wolfgang", "Walter", "Loke", "Waldemar", "Adam", "Gunda", "Hartmut", "Jochen", "Severin", "Elmar"]
    female_names = ["Agnes", "Sylvia", "Karla", "Erika", "Felicitas", "Emma", "Simone", "Linda", "Erika", "Miriam"]
    return random.choice(male_names + female_names)


def rand_last_name():
    ger_last_names = ["Fenstermacher", "Achterberg", "Bergmann", "Reich", "Werner", "Hochberg", "Bruhn", "Schlosser"]
    common_last_names = ["Peters", "Hofer"]
    last_names = ["Essert", "Simons", "Gross", "Mangold", "Sander", "Lorentz", "Hoffmann", "Hennig", "Beyer"]
    return random.choice(ger_last_names + common_last_names + last_names)


def rand_birthday():
    """
    :return: valid birthday that is 10..40 years in the past
    """
    random_number_of_days = random.randint(
        356 * 10,
        365 * 40,
    )
    return django.utils.timezone.make_aware(
        datetime.today() - timedelta(days=random_number_of_days),
    )


def _generate_superusers() -> None:
    users = [
        ("frank", "130120", "Frank", "Elsinga", "elsinga@example.com"),
        ("password", "username", "Nelson 'Big Head'", "Bighetti", "bighetti@example.com"),
    ]
    for username, password, first_name, last_name, email in users:
        get_user_model().objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            email=email,
            date_joined=django.utils.timezone.make_aware(datetime.today()),
        )
