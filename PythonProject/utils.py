from datetime import datetime

def update_date(date):
    timestamp_seconds = date / 1000.0
    date_time = datetime.fromtimestamp(timestamp_seconds)
    return date_time.strftime('%Y-%m-%d')
