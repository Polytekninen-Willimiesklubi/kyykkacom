import csv
import io
from datetime import datetime

from django.utils import timezone

from kyykka import models


def parse_match_file(
    uploaded_file,
    *,
    season,
    delimiter,
    datetime_format,
    date_column,
    home_column,
    away_column,
    field_column,
    has_header,
):
    try:
        content = uploaded_file.read().decode("utf-8-sig")
    except UnicodeDecodeError:
        return [], ["File must be UTF-8 encoded."]

    season_teams = {}
    for team in models.TeamsInSeason.objects.filter(season=season):
        season_teams.setdefault(team.current_abbreviation, []).append(team)

    parsed_rows = []
    errors = []
    reader = csv.reader(io.StringIO(content), delimiter=delimiter, strict=True)
    if has_header:
        next(reader, None)

    try:
        for row in reader:
            line_number = reader.line_num
            if not row or all(not value.strip() for value in row):
                continue

            mapped_columns = [date_column, home_column, away_column]
            if field_column is not None:
                mapped_columns.append(field_column)
            if len(row) <= max(mapped_columns):
                errors.append(f"Row {line_number}: not enough columns.")
                continue

            try:
                match_time = datetime.strptime(
                    row[date_column].strip(), datetime_format
                )
                match_time = timezone.make_aware(
                    match_time, timezone.get_current_timezone()
                )
            except (ValueError, OverflowError):
                errors.append(
                    f"Row {line_number}: date/time does not match the selected format."
                )
                continue

            if str(match_time.year) != season.year:
                errors.append(
                    f"Row {line_number}: date year {match_time.year} does not match "
                    f"selected season {season.year}."
                )
                continue

            home_abbreviation = row[home_column].strip()
            away_abbreviation = row[away_column].strip()
            home_matches = season_teams.get(home_abbreviation, [])
            away_matches = season_teams.get(away_abbreviation, [])
            if len(home_matches) != 1:
                errors.append(
                    f"Row {line_number}: home team '{home_abbreviation}' "
                    f"{'was not found' if not home_matches else 'is ambiguous'} "
                    f"in season {season.year}."
                )
                continue
            if len(away_matches) != 1:
                errors.append(
                    f"Row {line_number}: away team '{away_abbreviation}' "
                    f"{'was not found' if not away_matches else 'is ambiguous'} "
                    f"in season {season.year}."
                )
                continue

            field = None
            if field_column is not None and row[field_column].strip():
                try:
                    field = int(row[field_column].strip())
                except ValueError:
                    errors.append(f"Row {line_number}: field must be a whole number.")
                    continue

            home_team = home_matches[0]
            away_team = away_matches[0]
            parsed_rows.append(
                {
                    "line": line_number,
                    "match_time": match_time.isoformat(),
                    "home_team_id": home_team.pk,
                    "home_abbreviation": home_team.current_abbreviation,
                    "away_team_id": away_team.pk,
                    "away_abbreviation": away_team.current_abbreviation,
                    "field": field,
                }
            )
    except csv.Error as error:
        errors.append(f"CSV parsing error near row {reader.line_num}: {error}")

    if not parsed_rows and not errors:
        errors.append("The file contains no match rows.")

    seen_matches = set()
    for row in parsed_rows:
        match_key = (
            row["match_time"],
            row["home_team_id"],
            row["away_team_id"],
        )
        if match_key in seen_matches:
            errors.append(f"Row {row['line']}: duplicate match in uploaded file.")
        seen_matches.add(match_key)

    existing_lines = find_existing_match_lines(parsed_rows, season)
    errors.extend(
        f"Row {line_number}: this match already exists in the selected season."
        for line_number in existing_lines
    )
    return parsed_rows, errors


def find_existing_match_lines(rows, season):
    if not rows:
        return []

    match_times = [datetime.fromisoformat(row["match_time"]) for row in rows]
    home_team_ids = {row["home_team_id"] for row in rows}
    away_team_ids = {row["away_team_id"] for row in rows}
    existing_matches = models.Match.objects.filter(
        season=season,
        match_time__in=match_times,
        home_team_id__in=home_team_ids,
        away_team_id__in=away_team_ids,
    ).values_list("match_time", "home_team_id", "away_team_id")
    existing_keys = {
        (match_time, home_team_id, away_team_id)
        for match_time, home_team_id, away_team_id in existing_matches
    }
    return [
        row["line"]
        for row in rows
        if (
            datetime.fromisoformat(row["match_time"]),
            row["home_team_id"],
            row["away_team_id"],
        )
        in existing_keys
    ]
