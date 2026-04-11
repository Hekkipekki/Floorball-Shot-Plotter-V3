import csv
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
    ENTRY_LENGTH,
)


def save_csv(path, entries):
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "#", "S/G", "Phase", "Situation", "Shot Type", "Passer", "Shooter",
            "Period", "xG", "X", "Y", "Pass X", "Pass Y"
        ])

        for e in entries:
            row = list(e) + [None] * (ENTRY_LENGTH - len(e))

            writer.writerow([
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
                round(row[IDX_PASS_X], 2) if row[IDX_PASS_X] is not None else "",
                round(row[IDX_PASS_Y], 2) if row[IDX_PASS_Y] is not None else "",
            ])


def load_csv(path):
    entries = []

    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)

        for row in reader:
            if len(row) >= 11:
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
                entry[IDX_PASS_X] = float(row[11]) if len(row) > 11 and row[11] else None
                entry[IDX_PASS_Y] = float(row[12]) if len(row) > 12 and row[12] else None
                entry[IDX_VIDEO] = None

                entries.append(tuple(entry))

    return entries