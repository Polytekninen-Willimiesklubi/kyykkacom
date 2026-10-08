from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from kyykka import models
from kyykka.match_import import parse_match_file


class MatchImportTests(TestCase):
    def setUp(self):
        self.season = models.Season.objects.create(year="2023")
        self.home_team = models.Team.objects.create(name="Home team", abbreviation="H")
        self.away_team = models.Team.objects.create(name="Away team", abbreviation="A")
        models.TeamsInSeason.objects.create(
            season=self.season,
            team=self.home_team,
            current_name="Home team",
            current_abbreviation="H",
        )
        models.TeamsInSeason.objects.create(
            season=self.season,
            team=self.away_team,
            current_name="Away team",
            current_abbreviation="A",
        )

    def parse(self, content, **overrides):
        options = {
            "season": self.season,
            "delimiter": ",",
            "datetime_format": "%Y-%m-%d %H:%M:%S",
            "date_column": 0,
            "home_column": 1,
            "away_column": 2,
            "field_column": 3,
            "has_header": False,
        }
        options.update(overrides)
        uploaded_file = SimpleUploadedFile("matches.csv", content.encode("utf-8"))
        return parse_match_file(uploaded_file, **options)

    def test_parses_rows_with_custom_delimiter_and_column_mapping(self):
        rows, errors = self.parse(
            "H;2023-02-22 17:00;A;2\n",
            delimiter=";",
            datetime_format="%Y-%m-%d %H:%M",
            date_column=1,
            home_column=0,
            away_column=2,
            field_column=3,
        )

        self.assertEqual(errors, [])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["home_abbreviation"], "H")
        self.assertEqual(rows[0]["away_abbreviation"], "A")
        self.assertEqual(rows[0]["field"], 2)

    def test_rejects_year_mismatch_and_unknown_team(self):
        rows, errors = self.parse("2024-02-22 17:00:00,H,missing,2\n")

        self.assertEqual(rows, [])
        self.assertTrue(
            any("does not match selected season" in error for error in errors)
        )

    def test_rejects_match_that_already_exists(self):
        home_team = models.TeamsInSeason.objects.get(current_abbreviation="H")
        away_team = models.TeamsInSeason.objects.get(current_abbreviation="A")
        models.Match.objects.create(
            season=self.season,
            match_time="2023-02-22T17:00:00+02:00",
            home_team=home_team,
            away_team=away_team,
            field=2,
        )

        rows, errors = self.parse("2023-02-22 17:00:00,H,A,2\n")

        self.assertEqual(len(rows), 1)
        self.assertTrue(any("already exists" in error for error in errors))
