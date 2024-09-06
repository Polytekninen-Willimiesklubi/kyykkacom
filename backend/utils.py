from django.db.models import Count, Sum, F, Q, Case, Value, When, IntegerField, QuerySet
from django.db.models.functions import Cast, Substr
from .models import Throw, Season

def count_negative_values(throws: QuerySet | list[Throw], season: Season) -> int:
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

def count_throw_results(throws: QuerySet | list[Throw], result: str | int) -> int:
    result_total = throws.annotate(
        count = Count('pk', filter=Q(score_first=result)) + 
                Count('pk', filter=Q(score_second=result)) +
                Count('pk', filter=Q(score_third=result)) + 
                Count('pk', filter=Q(score_fourth=result))
    ).aggregate(Sum('count'))['count__sum']
    return result_total or 0

def count_score_total(throws: QuerySet | list[Throw]) -> int:
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


def count_gte_six_throw_results(throws: QuerySet | list[Throw]) -> int:
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

def calculate_scaled_points(throws: QuerySet | list[Throw]) -> int:
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