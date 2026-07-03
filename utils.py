from datetime import datetime

def format_date(date_string):

    dt = datetime.strptime(
        date_string,
        "%Y-%m-%d %H:%M"
    )

    now = datetime.now()

    delta = now - dt

    if delta.days == 0:

        if delta.seconds < 60:
            return "Just now"

        if delta.seconds < 3600:
            return f"{delta.seconds//60} min ago"

        return "Today"

    if delta.days == 1:
        return "Yesterday"

    return dt.strftime("%b %d")