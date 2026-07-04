import csv
from core.entry_helpers import normalize_entry
from core.schema import (
    IDX_NUMBER,
    IDX_RESULT,
    IDX_PHASE,
    IDX_SITUATION,
    IDX_TYPE,
    IDX_PASSER,
    IDX_SHOOTER,
    IDX_PERIOD,
    IDX_XG,
    IDX_X,
    IDX_Y,
    IDX_PASS_X,
    IDX_PASS_Y,
    IDX_VIDEO,
    IDX_DISTANCE,
    IDX_ANGLE,
    IDX_ZONE,
    ENTRY_LENGTH,
)

CSV_HEADERS = [
    "#", "S/G", "Phase", "Situation", "Shot Type", "Passer", "Shooter",
    "Period", "xG", "X", "Y", "Pass X", "Pass Y", "Distance", "Angle", "Zone",
]
MIN_CSV_COLUMNS = 11


def _padded_entry(entry):
    return normalize_entry(entry)


def _rounded_or_blank(value):
    return round(value, 2) if value is not None else ""


def _optional_float(row, index):
    return float(row[index]) if len(row) > index and row[index] else None


def _optional_text(row, index):
    return row[index] if len(row) > index else ""


def _entry_to_csv_row(entry):
    row = _padded_entry(entry)
    return [
        row[IDX_NUMBER],
        row[IDX_RESULT],
        row[IDX_PHASE],
        row[IDX_SITUATION],
        row[IDX_TYPE],
        row[IDX_PASSER],
        row[IDX_SHOOTER],
        row[IDX_PERIOD],
        row[IDX_XG],
        round(row[IDX_X], 2),
        round(row[IDX_Y], 2),
        _rounded_or_blank(row[IDX_PASS_X]),
        _rounded_or_blank(row[IDX_PASS_Y]),
        _rounded_or_blank(row[IDX_DISTANCE]),
        _rounded_or_blank(row[IDX_ANGLE]),
        row[IDX_ZONE],
    ]


def _csv_row_to_entry(row):
    entry = [None] * ENTRY_LENGTH
    entry[IDX_NUMBER] = int(row[0])
    entry[IDX_RESULT] = row[1]
    entry[IDX_PHASE] = row[2]
    entry[IDX_SITUATION] = row[3]
    entry[IDX_TYPE] = row[4]
    entry[IDX_PASSER] = row[5]
    entry[IDX_SHOOTER] = row[6]
    entry[IDX_PERIOD] = row[7]
    entry[IDX_XG] = float(row[8])
    entry[IDX_X] = float(row[9])
    entry[IDX_Y] = float(row[10])
    entry[IDX_PASS_X] = _optional_float(row, 11)
    entry[IDX_PASS_Y] = _optional_float(row, 12)
    entry[IDX_VIDEO] = None
    entry[IDX_DISTANCE] = _optional_float(row, 13)
    entry[IDX_ANGLE] = _optional_float(row, 14)
    entry[IDX_ZONE] = _optional_text(row, 15)
    return tuple(normalize_entry(entry))


def save_csv(path, entries):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_HEADERS)

        for entry in entries:
            writer.writerow(_entry_to_csv_row(entry))


def load_csv(path):
    entries = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if len(row) >= MIN_CSV_COLUMNS:
                entries.append(_csv_row_to_entry(row))

    return entries
