from . import views
from django.urls import path, include

urlpatterns = [
    path("anime_series/", views.SeriesView.as_view()),
    path("anime_series/<int:pk>/", views.SeriesView.as_view()),
    path("anime_ui/", views.series_list_ui, name="anime-list-ui"),
    path("anime_ui/<int:pk>/", views.series_detail_ui, name="anime-detail-ui"),

    path("movie/", views.MovieView.as_view()),
    path("movie/<int:pk>/", views.MovieView.as_view()),
    path("movie_ui/", views.movie_list_ui, name="movie-list-ui"),
    path("movie_ui/<int:pk>/", views.movie_detail_ui, name="movie-detail-ui"),

]
