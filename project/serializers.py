from rest_framework import serializers
from .models import Series, Genre, Movie
from .utils import populate_series_data, populate_movie_data
import textwrap


class GenreSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=100)


class SeriesSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    about = serializers.CharField(required=False)

    genre = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    release_year = serializers.IntegerField(required=False)

    poster = serializers.URLField(required=False, allow_null=True)
    imdb_link = serializers.URLField(required=False, allow_null=True)
    rt_link = serializers.URLField(required=False, allow_null=True)
    crunchyroll = serializers.URLField(required=False, allow_null=True)

    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "name": instance.name,
            "about": None,
            "release_year": instance.release_year,
            "poster": instance.poster,
            "imdb_link": instance.imdb_link,
            "rt_link": instance.rt_link,
            "crunchyroll": instance.crunchyroll,
            "genre": [
                {
                    # "id": g.id,
                    "name": g.name
                }
                for g in instance.genre.all()
            ],
        }

        if instance.about:
            clean_text = instance.about.replace("\r", " ").replace("\n", " ").strip()
            data["about"] = textwrap.wrap(clean_text, width=100)

        return data

    def create(self, validated_data):
        user_genres = validated_data.pop("genre", None)

        fetched = populate_series_data(validated_data["name"])

        fetched_genres = []
        if fetched:
            fetched_genres = fetched.pop("genre", [])
            for key, value in fetched.items():
                validated_data.setdefault(key, value)

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

    # =====================
    # UPDATE (PATCH / PUT)
    # =====================
    def update(self, instance, validated_data):
        genre_data = validated_data.pop("genre", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if genre_data is not None:
            genre_objs = []
            for g in genre_data:
                name = g.get("name") if isinstance(g, dict) else g
                if name:
                    obj, _ = Genre.objects.get_or_create(name=name)
                    genre_objs.append(obj)

            instance.genre.set(genre_objs)

        return instance


class MovieSerializer(serializers.Serializer):
    movie_name = serializers.CharField(max_length=255)
    about = serializers.CharField(required=False)

    # WRITE: genre as simple list of strings
    genre = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )

    release_year = serializers.IntegerField(required=False)

    poster = serializers.URLField(required=False, allow_null=True)
    imdb_link = serializers.URLField(required=False, allow_null=True)
    rt_link = serializers.URLField(required=False, allow_null=True)
    crunchyroll = serializers.URLField(required=False, allow_null=True)

    # WRITE: series by id
    series = serializers.PrimaryKeyRelatedField(
        queryset=Series.objects.all(), required=False, allow_null=True
    )

    # =====================
    # READ REPRESENTATION
    # =====================
    def to_representation(self, instance):
        data = {
            "id": instance.id,
            "movie_name": instance.movie_name,
            "about": None,
            "release_year": instance.release_year,
            "poster": instance.poster,
            "imdb_link": instance.imdb_link,
            "rt_link": instance.rt_link,
            "crunchyroll": instance.crunchyroll,
            "series": (
                {"name": instance.series.name}
                if instance.series
                else None
            ),
            "genre": [{"name": g.name} for g in instance.genre.all()],
        }

        if instance.about:
            clean_text = instance.about.replace("\r", " ").replace("\n", " ").strip()
            data["about"] = textwrap.wrap(clean_text, width=100)

        return data

    # =====================
    # CREATE
    # =====================
    def create(self, validated_data):
        user_genres = validated_data.pop("genre", None)
        series_obj = validated_data.pop("series", None)

        fetched = populate_movie_data(validated_data.get("movie_name"))

        if fetched:
            fetched_genres = fetched.pop("genre", [])
            for key, value in fetched.items():
                validated_data.setdefault(key, value)
        else:
            fetched_genres = []

        movie = Movie.objects.create(series=series_obj, **validated_data)

        # user > fetched priority
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

    def update(self, instance, validated_data):
        genre_data = validated_data.pop("genre", None)
        series_obj = validated_data.pop("series", None)

        if series_obj is not None:
            instance.series = series_obj

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if genre_data is not None:
            genre_objs = []
            for g in genre_data:
                name = g.get("name") if isinstance(g, dict) else g
                if name:
                    obj, _ = Genre.objects.get_or_create(name=name)
                    genre_objs.append(obj)
            instance.genre.set(genre_objs)

        return instance
