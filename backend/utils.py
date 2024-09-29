from django.db.models import Count, Sum, F, Q, Case, Value, When, IntegerField, QuerySet
from django.db.models.functions import Cast, Substr

def count_negative_values(throws: QuerySet, season) -> int:
    """From years 2012 and prior count and return pikes and zeros."""
    if int(season.year) > 2012:
        return (0,0)
    result_total = throws.annotate(
        count = Count('pk', filter=Q(score_first__contains=chr(8722))) + 
                Count('pk', filter=Q(score_second__contains=chr(8722))) +
                Count('pk', filter=Q(score_third__contains=chr(8722))) + 
                Count('pk', filter=Q(score_fourth__contains=chr(8722))),
        h = (Case(
            When(score_first__contains=chr(8722), then=Substr('score_first',2, 1)),
            default=Value(0),
            output_field=IntegerField(),
        ) + Case(
            When(score_second__contains=chr(8722), then=Substr('score_second',2, 1)),
            default=Value(0),
            output_field=IntegerField(),
        ) + Case(
            When(score_third__contains=chr(8722), then=Substr('score_third',2, 1)),
            default=Value(0),
            output_field=IntegerField(),
        ) + Case(
            When(score_fourth__contains=chr(8722), then=Substr('score_fourth',2, 1)),
            default=Value(0),
            output_field=IntegerField()
        )) / (Count('pk', filter=Q(score_first__contains=chr(8722))) + 
                Count('pk', filter=Q(score_second__contains=chr(8722))) +
                Count('pk', filter=Q(score_third__contains=chr(8722))) + 
                Count('pk', filter=Q(score_fourth__contains=chr(8722))))
    ).aggregate(Sum('h'), Sum('count'))
    pikes = result_total['h__sum'] or 0
    zeros = result_total['count__sum'] or 0
    return (pikes, zeros - pikes)

def count_throw_results(throws: QuerySet, result: str | int) -> int:
    result_total = throws.annotate(
        count = Count('pk', filter=Q(score_first=result)) + 
                Count('pk', filter=Q(score_second=result)) +
                Count('pk', filter=Q(score_third=result)) + 
                Count('pk', filter=Q(score_fourth=result))
    ).aggregate(Sum('count'))['count__sum']
    return result_total or 0

def count_score_total(throws: QuerySet) -> int:
    score_total = throws.annotate(
        st = Case(
            When(score_first__gte=0, then=F('score_first')),
            default=Value(0),
            output_field=IntegerField(),
        ),
        nd = Case(
            When(score_second__gte=0, then=F('score_second')),
            default=Value(0),
            output_field=IntegerField(),
        ),
        rd =Case(
            When(score_third__gte=0, then=F('score_third')),
            default=Value(0),
            output_field=IntegerField(),
        ),
        th = Case(
            When(score_fourth__gte=0, then=F('score_fourth')),
            default=Value(0),
            output_field=IntegerField(),
        )
    ).annotate(
        score = F('st') + F('nd') + F('rd') + F('th')
    ).aggregate(Sum('score'))['score__sum']
    return score_total or 0


def count_gte_six_throw_results(throws: QuerySet) -> int:
    result_total = throws.annotate(
        st = Cast("score_first", output_field=IntegerField()),
        nd = Cast("score_second", output_field=IntegerField()),
        rd = Cast("score_third", output_field=IntegerField()),
        th = Cast("score_fourth", output_field=IntegerField()),
    ).annotate(
        count = Count('pk', filter=Q(st__gte=6)) + 
                Count('pk', filter=Q(nd__gte=6)) +
                Count('pk', filter=Q(rd__gte=6)) + 
                Count('pk', filter=Q(th__gte=6))
    ).aggregate(Sum('count'))['count__sum']
    return result_total or 0

def calculate_scaled_points(throws: QuerySet) -> int:
    points = throws.annotate(
        st = Cast("score_first", output_field=IntegerField()),
        nd = Cast("score_second", output_field=IntegerField()),
        rd = Cast("score_third", output_field=IntegerField()),
        th = Cast("score_fourth", output_field=IntegerField())
    ).annotate(
        scaled_points = 
            ( F('st') * (9 + F('throw_turn')) ) / 5 +
            ( F('nd') * (9 + F('throw_turn')) ) / 5 +
            ( F('rd') * (13 + F('throw_turn')) ) / 5 +
            ( F('th') * (13 + F('throw_turn')) ) / 5
    ).aggregate(Sum('scaled_points'))['scaled_points__sum']
    return points or 0


MATCH_TYPES = [
    (1, "Runkosarja"),
    (2, "Finaali"),
    (3, "Pronssi"),
    (4, "Välierä"),
    (5, "Puolivälierä"),
    (6, "Neljännesvälierä"),
    (7, "Kahdeksannesvälierä"),
    (10, "Runkosarjafinaali"),
    (20, "Jumbofinaali"),
]

SUPER_WEEKEND_MATCHES = [
    (31, "Alkulohko"),
    (32, "Finaali"),
    (33, "Pronssi"),
    (34, "Välierä"),
    (35, "Puolivälierä"),
    (36, "Neljännesvälierä"),
    (37, "Kahdeksannesvälierä"),
]


PLAYOFF_FORMAT = [
    (0, 'Ei vielä päätetty / Undefined'),
    (1, "Kiinteä 16 joukkueen Cup"),
    (2, "Kiinteä 8 joukkueen Cup"),
    (3, "Kiinteä 4 joukkueen Cup"),
    (4, "Kiinteä 22 joukkueen Cup"),
    (5, "1.Kierroksen Seedaus 6 joukkueen Cup"),
    (6, "1.Kierroksen Seedaus 12 joukkueen Cup"),
    (7, "SuperWeekend OKA seedaus 15 joukkueen Cup"),
]

DIVISIONS = [
    (0, "A-Sarja"),
    (1, "B-Sarja")
]


def scaled_points(score: int, position: int):
    """Based on original kyykacom formula and it's mentioned Henna Pekkala's undergard:
    https://lutpub.lut.fi/bitstream/handle/10024/159742/Kandidaatintyo_Pekkala_Henna.pdf

    Because accuracy is not in scale points and rather it's in kyykkas, this formula is 
    the scaled by 2 for our purposes.
    
    Unscaled formula for reference:

    `points = 2n(w + h) / 10` , where 
    
    n=points, w=scaler, h=throw turn

    Scaler is:
    - 9, if 1st or 2nd throw
    - 13, if 3rd or 4th throw
    """
    w = 9 if position in [1,2] else 13
    return score * (w + position) / 10