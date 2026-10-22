from datetime import UTC, datetime


def now_iso_8601():
    now = datetime.now(tz=UTC)
    return now.strftime("%Y-%m-%dT%H:%M:%SZ")
