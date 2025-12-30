from typing import Literal

from django.db.models import (
    Case,
    Count,
    F,
    FloatField,
    IntegerField,
    Q,
    SmallIntegerField,
    Value,
    When,
)
from django.db.models.functions import Cast, Round

score_fields = ("score_first", "score_second", "score_third", "score_fourth")
casted_score_fields = ("st", "nd", "rd", "th")


def count_field_total(
    val: int | str, *fields: str, gte: bool = False
) -> Count | Literal[0]:
    """Returns sum of the total counts of each field with the given value."""
    if gte:
        fields = tuple(f"{field}__gte" for field in fields)
    return sum(Count("pk", filter=Q(**{field: val})) for field in fields)


def rounded_divison(
    numer_field: str, denom_field: str, percentage: bool = False
) -> Round | Value:
    """Returns the rounded (2 decimals) division of numerator by denominator.
    If denominator is zero, returns NaN.
    """
    return (
        Round(
            F(numer_field) / F(denom_field) * 100
            if percentage
            else F(numer_field) / F(denom_field),
            precision=2,
            output_field=FloatField(),
        )
        if F(denom_field)
        else Value("NaN")
    )


def scaled_points() -> F:
    """Returns players scaled points for one throw round.

    This is designed for spesfically to `Throw` - model after casting the each throw to int.
    """
    return (
        (F("st") + F("nd")) * (9 + F("throw_turn"))
        + (F("rd") + F("th")) * (13 + F("throw_turn"))
    ) / 5


def scores_casted_to_int() -> dict[str, Cast]:
    """Returns the score fields casted to integer."""
    return {
        cast: Cast(F(org), IntegerField())
        for cast, org in zip(casted_score_fields, score_fields)
    }


def count_non_throws() -> Case | Literal[0]:
    """Returns the count of non-throws in a throw round."""
    return sum(Case(When(**{field: "e"}, then=1), default=0) for field in score_fields)


def get_correct_round_score() -> Case:
    """Returns the correct score for the throw round based on the team.

    Round score is determined by the team (home or away) and the throw round (1 or 2).
    """
    return Case(
        When(
            match__home_team=F("team"),
            then=Case(
                When(throw_round=1, then=F("match__home_first_round_score")),
                default=F("match__home_second_round_score"),
            ),
        ),
        When(
            match__away_team=F("team"),
            then=Case(
                When(throw_round=1, then=F("match__away_first_round_score")),
                default=F("match__away_second_round_score"),
            ),
        ),
        output_field=SmallIntegerField(),
    )


def get_correct_match_score() -> Case:
    """Returns the correct score for the throw rounds' match based on the team.

    Match score is determined by the team (home or away) and the throw round (1 or 2).
    """
    return Case(
        When(
            match__home_team=F("team"),
            then=F("match__home_first_round_score")
            + F("match__home_second_round_score"),
        ),
        default=F("match__away_first_round_score")
        + F("match__away_second_round_score"),
        output_field=SmallIntegerField(),
    )
