import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db

class TestMeeting:
    def test_init(self):
        obj = mixer.blend('meetings.Meeting')
        assert obj.pk not in (None, ""), 'Should create a Meeting instance'
