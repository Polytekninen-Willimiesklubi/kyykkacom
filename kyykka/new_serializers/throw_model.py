"""Serializers for `Throw` model"""

from django.db.models import F, IntegerField, QuerySet, Sum
from django.db.models.functions import Cast
from rest_framework import serializers

from kyykka.serializers import Throw


class ThrowsSummary(serializers.ModelSerializer):
    """Serializer to aggregate `Throw`-model to statistics"""

    score_total = serializers.SerializerMethodField()
    match_count = serializers.SerializerMethodField()
    round_count = serializers.SerializerMethodField()
    # pikes = serializers.SerializerMethodField()

    def get_score_total(self, obj: QuerySet[Throw]) -> int:
        total = obj.annotate(
            st=Cast("score_first", output_field=IntegerField()),
            nd=Cast("score_second", output_field=IntegerField()),
            rd=Cast("score_third", output_field=IntegerField()),
            th=Cast("score_fourth", output_field=IntegerField()),
        ).aggregate(score=Sum(F("st") + F("nd") + F("rd") + F("th")))["score__sum"]
        return total or 0

    def get_match_count(self, obj: QuerySet[Throw]) -> int:
        total = obj.values("match").distinct().count()
        return total or 0

    def get_round_count(self, obj: QuerySet[Throw]) -> int:
        total = obj.values("match").count()
        return total or 0

    # def get_pikes(self, obj: QuerySet[Throw]) -> int:
    #     all_score_counts = obj.values(
    #         "score_first", "score_second", "score_third", "score_fourth"
    #     ).annotate(
    #         st=Count("score_first"),
    #         nd=Count("score_second"),
    #         rd=Count("score_third"),
    #         th=Count("score_fourth"),
    #     )
    #     print("")

    class Meta:
        model = Throw
        fields = "__all__"
