from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    deleted_at = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True

    def soft_delete(self):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])


class Genre(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Series(BaseModel):
    name = models.CharField(max_length=255)
    about = models.TextField()
    genre = models.ManyToManyField(Genre)
    release_year = models.IntegerField(null=True, blank=True)
    poster = models.URLField(null=True, blank=True)

    # Info
    imdb_link = models.URLField(null=True, blank=True)
    rt_link = models.URLField(null=True, blank=True)

    # Streaming (ONLY THESE 3)
    crunchyroll = models.URLField(null=True, blank=True)
    tmdb = models.URLField(null=True, blank=True)

    def __str__(self):
        return self.name


class Movie(BaseModel):
    movie_name = models.CharField(max_length=255)
    about = models.TextField(blank=True)

    series = models.ForeignKey(
        Series,
        on_delete=models.SET_DEFAULT,
        default=1,
        related_name="movies",
        null=True,
        blank=True,
    )

    genre = models.ManyToManyField(Genre, blank=True)
    release_year = models.IntegerField(null=True, blank=True)
    poster = models.URLField(null=True, blank=True)

    # Info
    imdb_link = models.URLField(null=True, blank=True)
    tmdb = models.URLField(null=True, blank=True)
    rt_link = models.URLField(null=True, blank=True)

    # Streaming (ONLY THESE 3)
    crunchyroll = models.URLField(null=True, blank=True)
    def __str__(self):
        return self.movie_name
