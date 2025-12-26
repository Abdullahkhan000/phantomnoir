import django_filters
from .models import Series , Movie


class SeriesFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    genre = django_filters.CharFilter(
        field_name="genres__name", lookup_expr="icontains"
    )
    released_after = django_filters.NumberFilter(
        field_name="release_year", lookup_expr="gte"
    )
    released_before = django_filters.NumberFilter(
        field_name="release_year", lookup_expr="lte"
    )

    class Meta:
        model = Series
        fields = ["name", "genre", "released_after", "released_before"]


class MovieFilter(django_filters.FilterSet):
    movie_name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")
    genre = django_filters.CharFilter(
        field_name="genre__name", lookup_expr="icontains"
    )
    released_after = django_filters.NumberFilter(
        field_name="release_year", lookup_expr="gte"
    )
    released_before = django_filters.NumberFilter(
        field_name="release_year", lookup_expr="lte"
    )

    class Meta:
        model = Movie
        fields = ["movie_name", "genre", "released_after", "released_before"]