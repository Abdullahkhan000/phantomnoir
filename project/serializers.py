from rest_framework import serializers
from .models import Series, Genre, Movie
from .utils import populate_series_data, populate_movie_data
import textwrap


class GenreSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)

class SeriesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    genre = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    release_year = serializers.IntegerField(required=False, allow_null=True)
    poster = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    imdb_link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    rt_link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    tmdb = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    crunchyroll = serializers.URLField(required=False, allow_null=True, allow_blank=True)

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "name": instance.name,
            "about": None,
            "release_year": instance.release_year,
            "poster": instance.poster,
            "imdb_link": instance.imdb_link,
            "rt_link": instance.rt_link,
            "tmdb": instance.tmdb,
            "crunchyroll": instance.crunchyroll,
            "genre": [{"name": g.name} for g in instance.genre.all()],
        }
        if instance.about:
            clean_text = instance.about.replace("\r", " ").replace("\n", " ").strip()
            data["about"] = textwrap.wrap(clean_text, width=100)
        return data

    def create(self, validated_data):
        user_genres = validated_data.pop("genre", None)
        series_name = validated_data.get("name")

        fetched = populate_series_data(series_name)

        if fetched:
            fetched_genres = fetched.pop("genre", [])
            for key, value in fetched.items():
                if value:
                    validated_data.setdefault(key, value)
        else:
            fetched_genres = []

        if not validated_data.get("release_year"):
            validated_data["release_year"] = 0

        series = Series.objects.create(**validated_data)

        all_genres = user_genres if user_genres is not None else fetched_genres
        genre_objs = []
        for g in all_genres or []:
            name = g.get("name") if isinstance(g, dict) else g
            if name:
                obj, _ = Genre.objects.get_or_create(name=name)
                genre_objs.append(obj)

        if genre_objs:
            series.genre.set(genre_objs)
        return series

class MovieSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    movie_name = serializers.CharField(max_length=255)
    about = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    genre = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )
    release_year = serializers.IntegerField(required=False, allow_null=True)
    poster = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    imdb_link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    rt_link = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    tmdb = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    crunchyroll = serializers.URLField(required=False, allow_null=True, allow_blank=True)
    series = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), required=False, allow_null=True
    )

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "movie_name": instance.movie_name,
            "about": None,
            "release_year": instance.release_year,
            "poster": instance.poster,
            "imdb_link": instance.imdb_link,
            "rt_link": instance.rt_link,
            "tmdb": instance.tmdb,
            "crunchyroll": instance.crunchyroll,
            "series": ({"name": instance.series.name} if instance.series else None),
            "genre": [{"name": g.name} for g in instance.genre.all()],
        }
        if instance.about:
            clean_text = instance.about.replace("\r", " ").replace("\n", " ").strip()
            data["about"] = textwrap.wrap(clean_text, width=100)
        return data

    def create(self, validated_data):
        user_genres = validated_data.pop("genre", None)
        series_obj = validated_data.pop("series", None)
        movie_name = validated_data.get("movie_name")

        fetched = populate_movie_data(movie_name)
        if fetched:
            fetched_genres = fetched.pop("genre", [])
            for key, value in fetched.items():
                if value:
                    validated_data.setdefault(key, value)
        else:
            fetched_genres = []

        if not validated_data.get("release_year"):
            validated_data["release_year"] = 0

        movie = Movie.objects.create(series=series_obj, **validated_data)

        all_genres = user_genres if user_genres is not None else fetched_genres
        genre_objs = []
        for g in all_genres or []:
            name = g.get("name") if isinstance(g, dict) else g
            if name:
                obj, _ = Genre.objects.get_or_create(name=name)
                genre_objs.append(obj)

        if genre_objs:
            movie.genre.set(genre_objs)
        return movie