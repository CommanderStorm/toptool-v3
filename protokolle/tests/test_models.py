import pytest
from mixer.backend.django import mixer

pytestmark = pytest.mark.django_db


class TestMeeting:
    def test_init(self):
        obj = mixer.blend("protokolle.Protokoll")
        assert obj.pk not in (None, ""), "Should create a Protokoll instance"
