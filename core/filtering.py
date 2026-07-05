from core.schema import IDX_PERIOD

ALL_MATCHES = "All"
SEASON_MATCH = "Season"
SPECIAL_MATCHES = (ALL_MATCHES, SEASON_MATCH)


def individual_match_names(app):
    return [name for name in app.match_logs.keys() if name not in SPECIAL_MATCHES]


def combined_match_entries(app):
    if SEASON_MATCH in app.match_logs:
        return list(app.match_logs.get(SEASON_MATCH, []))

    entries = []
    for name in individual_match_names(app):
        entries.extend(app.match_logs.get(name, []))
    return entries


def selected_shotlog_match_names(app):
    all_var = getattr(app, "shotlog_match_filter_all", None)
    match_vars = getattr(app, "shotlog_match_filter_vars", None)

    if all_var is None or match_vars is None or all_var.get():
        return None

    selected = []
    for name, var in match_vars.items():
        if name in app.match_logs and var.get():
            selected.append(name)

    return selected or None


def get_match_entries(app, match):
    selected_matches = selected_shotlog_match_names(app)
    if selected_matches is not None:
        entries = []
        for name in selected_matches:
            entries.extend(app.match_logs.get(name, []))
        return entries

    if match in (ALL_MATCHES, SEASON_MATCH):
        return combined_match_entries(app)

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
