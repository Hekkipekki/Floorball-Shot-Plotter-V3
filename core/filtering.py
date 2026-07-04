from core.schema import IDX_PERIOD

ALL_MATCHES = "All"


def get_match_entries(app, match):
    if match == ALL_MATCHES:
        entries = []
        for logs in app.match_logs.values():
            entries.extend(logs)
        return entries
    return app.match_logs.get(match, [])


def filter_by_period(entries, period):
    if period == ALL_MATCHES:
        return entries
    return [e for e in entries if str(e[IDX_PERIOD]) == str(period)]


def get_filtered_entries(app):
    match = app.current_match.get()
    period = app.period_selected.get()

    entries = get_match_entries(app, match)
    return filter_by_period(entries, period)


def get_filtered_entries_by_period(app, period_filter):
    match = app.current_match.get()

    entries = get_match_entries(app, match)
    return filter_by_period(entries, period_filter)
