import random
import string
from datetime import timedelta
from subprocess import run  # nosec: used for flushing the db
from uuid import uuid4

import django.utils.timezone
import lorem
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user
from django.utils.datetime_safe import datetime

import meetings.models as meeting_models
import meetingtypes.models as mt_models
import persons.models as persons_models
import protokolle.models as protokolle_models
import tops.models as top_models
import userprofile.models as userprofile_models


def showroom_fixture_state():
    """
    Makes the database apply a fixture state.
    DELETES ALL DATA!
    """
    confirmation = input(
        "Do you really want to load the showroom fixture? (This will flush the database) [y/n]",
    )
    if confirmation.lower() != "y":
        return
    showroom_fixture_state_no_confirmation()


def showroom_fixture_state_no_confirmation():  # nosec: this is only used in a fixture
    """
    same as showroom_fixture_state but without confirmation
    """
    run(["python3", "manage.py", "flush", "--noinput"], check=True)

    # user
    _generate_superusers()

    # meetingtypes
    _generate_meetingtypes()

    # meetings
    _generate_meetings()

    # tops
    _generate_stdtops()
    _generate_tops()

    # persons

    # protokolle


def rand_company_name():
    """
    @return a random companyname
    """
    cool_names = ["Caliburst", "Ironhide", "Stylor", "Spectro", "Camshaft", "Haywire", "Snarl", "Starscream"]
    violent_names = ["Warpath", "Recoil", "Broadside", "Scattershot", "Thundercracker"]
    lame_names = ["Scrapper", "Streetwise", "Arcana", "Grax", "Drag Strip", "Chromedome", "Slag"]
    return random.choice(cool_names + violent_names + lame_names)


def rand_firstname():
    """
    @return a random firstname
    """
    male_names = ["Wolfgang", "Walter", "Loke", "Waldemar", "Adam", "Gunda", "Hartmut", "Jochen", "Severin", "Elmar"]
    female_names = ["Agnes", "Sylvia", "Karla", "Erika", "Felicitas", "Emma", "Simone", "Linda", "Erika", "Miriam"]
    return random.choice(male_names + female_names)


def rand_last_name():
    """
    @return a random lastname
    """
    ger_last_names = ["Fenstermacher", "Achterberg", "Bergmann", "Reich", "Werner", "Hochberg", "Bruhn", "Schlosser"]
    common_last_names = ["Peters", "Hofer"]
    last_names = ["Essert", "Simons", "Gross", "Mangold", "Sander", "Lorentz", "Hoffmann", "Hennig", "Beyer"]
    return random.choice(ger_last_names + common_last_names + last_names)


def rand_birthday():
    """
    @return valid birthday that is 10..40 years in the past
    """
    random_number_of_days = random.randint(
        356 * 10,
        365 * 40,
    )
    return django.utils.timezone.make_aware(
        datetime.today() - timedelta(days=random_number_of_days),
    )


def rand_user() -> User:
    """
    @return a random user
    """
    return random.choice(list(get_user_model().objects.all()))


def _generate_superusers() -> None:
    """
    Generates two superusers (frank and password)
    """
    user_values = [
        ("frank", "130120", "Frank", "Elsinga", "elsinga@example.com"),
        ("password", "username", "Nelson 'Big Head'", "Bighetti", "bighetti@example.com"),
    ]
    cm_dark = True
    users = []
    for username, password, first_name, last_name, email in user_values:
        users.append(get_user_model().objects.create(
            username=username,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            is_superuser=True,
            is_staff=True,
            is_active=True,
            email=email,
            date_joined=django.utils.timezone.make_aware(datetime.today()),
        ))
    # separated for race condition (Profile not yet created) to resolve
    for user in users:
        user.profile.cm_dark = userprofile_models.Profile.CM_DARK if cm_dark else userprofile_models.Profile.CM_LIGHT
        user.profile.save()
        cm_dark = not cm_dark


def _generate_meetingtypes() -> None:
    """
    Generates some meetingtypes for the meetings
    @return: None
    """
    mts = {
        "fsinfo": "Fachschaft Informatik",
        "fsma": "Fachschaft Mathematik",
        "fsph": "Fachschaft Physik",
        "asta": "Sitzung der Allgemeinen Studentischen Vertretung",
    }

    for shortname, name in mts.items():
        attendance = random.choice((True, True, True, False))
        mt_models.MeetingType.objects.create(
            name=name,
            id=shortname,
            mailinglist=f"{shortname}@fs.tum.de" if random.choice((True, True, False)) else None,
            defaultmeetingtitle=f"Sitzung der {name}",
            public=random.choice((True, False)),
            ical_key=random.choice((None, uuid4())),
            attendance=random.choice((True, True, True, False)),
            attendance_with_func=attendance and random.choice((True, True, False)),
            protokoll=random.choice((True, False)),
            write_protokoll_button=random.choice((True, True, False)),
            approve=random.choice((True, False)),
            motion_tag=random.choice((True, False)),
            point_of_order_tag=random.choice((True, False)),
            attachment_protokoll=random.choice((True, False)),
            pad_setting=random.choice((True, False)),
            tops=random.choice((True, False)),
            top_perms=random.choice(mt_models.MeetingType.TOP_PERMS)[0],
            top_user_edit=random.choice((True, True, True, False)),
            top_deadline=random.choice((True, False)),
            standard_tops=random.choice((True, True, False)),
            other_in_tops=random.choice((True, True, False)),
            attachment_tops=random.choice((True, True, False)),
            anonymous_tops=random.choice((True, True, False)),
            first_topid=random.choice([0] * 3 + [1] * 3 + [42]),
            custom_template="",
        )


def _generate_stdtops() -> None:
    """
    Generates some standard tops for the meetings
    @return:
    """
    meetingtype: mt_models.MeetingType
    for meetingtype in mt_models.MeetingType.objects.all():
        for i in range(random.randint(0, 3)):
            title_prefix = random.choice(["Beschluss von", "Ende von", "Start von", "Bezüglich"]) + " "
            top_models.StandardTop.objects.create(
                topid=i,
                title=title_prefix + lorem.sentence(),
                description=random.choice([lorem.sentence()] * 3 + [""]),
                protokoll_templ=random.choice([""] * 3 + ["Templated:"]),
                meetingtype=meetingtype,
            )


def _generate_tops() -> None:
    meeting: meeting_models.Meeting
    for meeting in meeting_models.Meeting.objects.all():
        for i in range(random.randint(1, 10)):
            first_name = rand_firstname()
            name = rand_last_name()
            prefix_choices = ["Beschluss von", "Kauf von", "Entzug von", "Ende von", "Start von", "Bezüglich"]
            title_prefix = f"{random.choice(prefix_choices)} "
            top_models.Top.objects.create(
                topid=i + 10,
                title=title_prefix + lorem.sentence(),
                description=random.choice([lorem.sentence()] * 3 + [""]),
                protokoll_templ=random.choice([""] * 3 + ["Templated:"]),
                meeting=meeting,
                user=random.choice((None, rand_user())),
                author=f"{first_name} {name}",
                email=f"{first_name.lower()}.{name.lower()}@fs.tum.de",
                attachment=None,  # TODO
            )


def _generate_meetings() -> None:
    meetingtype: mt_models.MeetingType
    for meetingtype in mt_models.MeetingType.objects.all():
        room = f"{random.randint(-1, 4):02}.{random.randint(0, 13):02}.{random.randint(0, 99):03}"
        if random.choice((True, False)):
            url_suffix = "".join(random.choice((random.choice(string.ascii_lowercase), "-")) for _ in range(10))
            room += " or in https://bbb.fs.tum.de/b/" + url_suffix
        for _ in range(random.randint(10, 30)):
            time_offset = timedelta(
                days=random.randint(-365, 365),
                hours=random.randint(0, 24),
                minutes=random.randint(0, 60),
            )
            time = django.utils.timezone.make_aware(datetime.today() - time_offset)
            meeting: meeting_models.Meeting = meeting_models.Meeting.objects.create(
                time=time,
                room=room,
                meetingtype=meetingtype,
                title=f"Konstituierende {meetingtype.defaultmeetingtitle}"
                if random.choice([False] * 10 + [True])
                else "",
                topdeadline=time + timedelta(days=random.randint(0, 2)) if random.choice((True, False)) else None,
                sitzungsleitung=rand_user() if random.choice((False, True)) else None,
                stdtops_created=False,
                imported=random.choice((True, False)),
                pad="",
            )
            if random.choice((False, True)):
                for _ in range(random.randint(1, 3)):
                    user: User = rand_user()
                    if user.id not in meeting.minute_takers.related_val:
                        meeting.minute_takers.add(user)
                meeting.save()
