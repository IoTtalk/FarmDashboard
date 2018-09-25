import datetime


def row2dict(row, str_datetime=True):
    """Convert query object by sqlalchemy to dictionary object."""
    if not row:
        return None

    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)
        if str_datetime and isinstance(d[column.name], datetime.datetime):
            d[column.name] = str(d[column.name])
    return d
