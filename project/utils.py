import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status
from .models import Series, Movie
from typing import Union

JIKAN_BASE_URL = "https://api.jikan.moe/v4"
TMDB_BASE_URL = "https://api.themoviedb.org/3"

OMDB_API_KEY = settings.OMDB_API_KEY
TMDB_API_KEY = settings.TMDB_API_KEY

def fetch_jikan_anime(title):
    url = f"{JIKAN_BASE_URL}/anime"
    params = {"q": title, "limit": 1}

    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200 or not resp.json().get("data"):
            return None

        anime = resp.json()["data"][0]

        release_year = anime.get("year") or anime.get("aired", {}).get("prop", {}).get("from", {}).get("year")

        crunchyroll_url = None
        for s in anime.get("streaming", []):
            if "crunchyroll" in s.get("name", "").lower():
                crunchyroll_url = s.get("url")
                break

        ext_resp = requests.get(f"{JIKAN_BASE_URL}/anime/{anime['mal_id']}/external")
        if ext_resp.status_code == 200:
            for link in ext_resp.json().get("data", []):
                if "crunchyroll" in link.get("name", "").lower() and not crunchyroll_url:
                    crunchyroll_url = link.get("url")

        return {
            "about": anime.get("synopsis"),
            "poster": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
            "release_year": release_year,
            "genre": [g["name"] for g in anime.get("genres", [])],
            "crunchyroll": crunchyroll_url,
        }

    except Exception as e:
        print("Jikan error:", e)
        return None


def fetch_omdb_imdb_link(title: str):
    try:
        url = "http://www.omdbapi.com/"
        params = {"t": title, "apikey": OMDB_API_KEY}
        resp = requests.get(url, params=params).json()

        if resp.get("Response") == "True" and resp.get("imdbID"):
            return f"https://www.imdb.com/title/{resp['imdbID']}/"
        return None

    except Exception as e:
        print("OMDb error:", e)
        return None


def generate_rt_link(title: str, media_type="movie"):
    clean = title.replace(" ", "_").replace(":", "").replace("-", "_").lower()
    rt_type = "m" if media_type == "movie" else "tv"
    return f"https://www.rottentomatoes.com/{rt_type}/{clean}"

def fetch_tmdb_streaming(title: str, media_type="tv", region="US"):
    result = {"tmdb": None}

    try:
        search_url = f"{TMDB_BASE_URL}/search/{media_type}"
        search = requests.get(
            search_url,
            params={"api_key": TMDB_API_KEY, "query": title}
        ).json()

        if not search.get("results"):
            return result

        tmdb_id = search["results"][0]["id"]
        result["tmdb"] = f"https://www.themoviedb.org/{media_type}/{tmdb_id}/watch?locale={region}"

        return result

    except Exception as e:
        print("TMDB streaming error:", e)
        return result

def populate_series_data(series_input: Union[Series, str]):
    series_obj = None
    name = series_input.name if isinstance(series_input, Series) else series_input

    if isinstance(series_input, Series):
        series_obj = series_input
    else:
        series_obj = Series.objects.filter(name=name).first()

    jikan = fetch_jikan_anime(name)
    streaming = fetch_tmdb_streaming(name, media_type="tv")

    imdb = series_obj.imdb_link if series_obj and series_obj.imdb_link else fetch_omdb_imdb_link(name)
    rt = series_obj.rt_link if series_obj and series_obj.rt_link else generate_rt_link(name, "tv")

    crunchyroll_link = jikan.get("crunchyroll") if jikan else None
    if not crunchyroll_link:
        crunchyroll_link = f"https://www.crunchyroll.com/search?q={name.replace(' ', '+')}"

    if series_obj:
        series_obj.imdb_link = imdb
        series_obj.rt_link = rt
        series_obj.tmdb = streaming["tmdb"]
        series_obj.crunchyroll = crunchyroll_link
        series_obj.save()

    return {
        "about": series_obj.about if series_obj else (jikan.get("about") if jikan else ""),
        "poster": series_obj.poster if series_obj else (jikan.get("poster") if jikan else None),
        "release_year": series_obj.release_year if series_obj else (jikan.get("release_year") if jikan else None),
        "genre": [g.name for g in series_obj.genre.all()] if series_obj else (jikan.get("genre") if jikan else []),
        "imdb_link": imdb,
        "rt_link": rt,
        "crunchyroll": crunchyroll_link,
        **streaming,
    }

def populate_movie_data(movie_input: Union[Movie, str]):
    movie_obj = None
    name = movie_input.movie_name if isinstance(movie_input, Movie) else movie_input

    if isinstance(movie_input, Movie):
        movie_obj = movie_input
    else:
        movie_obj = Movie.objects.filter(movie_name=name).first()

    jikan = fetch_jikan_anime(name)
    streaming = fetch_tmdb_streaming(name, media_type="movie")

    imdb = movie_obj.imdb_link if movie_obj and movie_obj.imdb_link else fetch_omdb_imdb_link(name)
    rt = movie_obj.rt_link if movie_obj and movie_obj.rt_link else generate_rt_link(name, "movie")

    crunchyroll_link = jikan.get("crunchyroll") if jikan else None
    if not crunchyroll_link:
        crunchyroll_link = f"https://www.crunchyroll.com/search?q={name.replace(' ', '+')}"

    if movie_obj:
        movie_obj.imdb_link = imdb
        movie_obj.rt_link = rt
        movie_obj.tmdb = streaming["tmdb"]
        movie_obj.crunchyroll = crunchyroll_link
        movie_obj.save()

    return {
        "about": movie_obj.about if movie_obj else (jikan.get("about") if jikan else ""),
        "poster": movie_obj.poster if movie_obj else (jikan.get("poster") if jikan else None),
        "release_year": movie_obj.release_year if movie_obj else (jikan.get("release_year") if jikan else None),
        "genre": [g.name for g in movie_obj.genre.all()] if movie_obj else (jikan.get("genre") if jikan else []),
        "imdb_link": imdb,
        "rt_link": rt,
        "crunchyroll": crunchyroll_link,
        **streaming,
    }

def get_obj_or_404(model, pk):
    if not pk:
        return None, Response({"error": "Primary key required"}, status=status.HTTP_400_BAD_REQUEST)
    try:
        return model.objects.get(pk=pk), None
    except model.DoesNotExist:
        return None, Response({"error": "Not found"}, status=status.HTTP_404_NOT_FOUND)
