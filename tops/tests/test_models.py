# pylint: disable=no-self-use
# pylint: disable=too-few-public-methods
import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestMeeting:
    def test_init(self):
        obj = mixer.blend("tops.Top")
        assert obj.pk not in (None, ""), "Should create a Top instance"
        obj = mixer.blend("tops.StandardTop")
        assert obj.pk not in (None, ""), "Should create a StandardTop instance"
