from ml.features.revision import get_current_revision


def test_get_current_revision():
    current_time_jst = "2022-01-01 00:00:00"
    assert get_current_revision(current_time_jst) == "2022/01/01/00"
