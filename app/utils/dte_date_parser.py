from datetime import datetime


def parse_dte_date(dte_date):
    """Parse a DTE date to a datetime object."""
    return datetime.strptime(dte_date, '%d/%m/%Y %H:%M:%S')
