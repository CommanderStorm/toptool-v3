# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestMeetingType:
    def test_init(self):
        obj = mixer.blend("meetingtypes.MeetingType")
        assert obj.pk not in (None, ""), "Should create a MeetingType instance"
