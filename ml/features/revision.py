import datetime as dt


def get_current_revision(current_time_jst: str) -> str:
    revision = dt.datetime.strptime(current_time_jst, "%Y-%m-%d %H:%M:%S")
    return revision.strftime("%Y/%m/%d/%H")
