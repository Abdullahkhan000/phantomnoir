import requests
from django.conf import settings
from rest_framework.response import Response
from rest_framework import status

TMDB_API_KEY = settings.TMDB_API_KEY
JIKAN_BASE_URL = "https://api.jikan.moe/v4"


def fetch_jikan_anime(title):
    print(f"\n--- Searching Jikan for: {title} ---")
    url = f"{JIKAN_BASE_URL}/anime"
    params = {"q": title, "limit": 1}

    try:
        resp = requests.get(url, params=params)
        if resp.status_code != 200 or not resp.json().get("data"):
            print(f"Jikan Error or No Data: {resp.status_code}")
            return None

        anime = resp.json()["data"][0]
        mal_id = anime["mal_id"]
        print(f"Found MAL ID: {mal_id}")

        imdb_url = None
        crunchyroll_url = None

        for s in anime.get("streaming", []):
            if "crunchyroll" in s.get("name", "").lower():
                crunchyroll_url = s.get("url")
                print("Crunchyroll found in streaming list.")
                break

        ext_resp = requests.get(f"{JIKAN_BASE_URL}/anime/{mal_id}/external")
        if ext_resp.status_code == 200:
            external_links = ext_resp.json().get("data", [])
            for link in external_links:
                site = link.get("name", "").lower()
                if "imdb" in site:
                    imdb_url = link.get("url")
                elif "crunchyroll" in site and not crunchyroll_url:
                    crunchyroll_url = link.get("url")

        release_year = anime.get("year")
        if not release_year:
            aired = anime.get("aired", {}).get("prop", {}).get("from", {})
            release_year = aired.get("year")

        print(f"Release Year Determined: {release_year}")

        return {
            "about": anime.get("synopsis"),
            "poster": anime.get("images", {}).get("jpg", {}).get("large_image_url"),
            "release_year": release_year,
            "genre": [g["name"] for g in anime.get("genres", [])],
            "imdb_link": imdb_url,
            "crunchyroll": crunchyroll_url,
        }
    except Exception as e:
        print(f"Jikan Helper Exception: {e}")
        return None


def fetch_tmdb_links(title, media_type="tv", year=None):
    print(f"Searching TMDB ({media_type}) for: {title}")
    search_url = f"https://api.themoviedb.org/3/search/{media_type}"
    params = {"api_key": TMDB_API_KEY, "query": title}

    if year:
        year_key = (
            "first_air_date_year" if media_type == "tv" else "primary_release_year"
        )
        params[year_key] = year

    try:
        resp = requests.get(search_url, params=params)
        data = resp.json()

        if not data.get("results") and year:
            print("No TMDB results with year, retrying without year filter...")
            params.pop("first_air_date_year", None)
            params.pop("primary_release_year", None)
            resp = requests.get(search_url, params=params)
            data = resp.json()

        imdb_link = None
        if data.get("results"):
            tmdb_id = data["results"][0]["id"]
            ext_url = (
                f"https://api.themoviedb.org/3/{media_type}/{tmdb_id}/external_ids"
            )
            ext_resp = requests.get(ext_url, params={"api_key": TMDB_API_KEY})
            if ext_resp.status_code == 200:
                imdb_id = ext_resp.json().get("imdb_id")
                if imdb_id:
                    imdb_link = f"https://www.imdb.com/title/{imdb_id}"

        clean_title = title.replace(" ", "_").replace(":", "").replace("-", "_").lower()
        rt_type = "m" if media_type == "movie" else "tv"
        rt_link = f"https://www.rottentomatoes.com/{rt_type}/{clean_title}"

        return {"imdb": imdb_link, "rt": rt_link}
    except Exception as e:
        print(f"TMDB Helper Exception: {e}")
        return {"imdb": None, "rt": None}


def populate_series_data(series_name):
    jikan = fetch_jikan_anime(series_name)
    if not jikan:
        return None

    tmdb = fetch_tmdb_links(series_name, media_type="tv", year=jikan["release_year"])

    final_imdb = jikan.get("imdb_link") or tmdb.get("imdb")
    if not final_imdb:
        print(f"IMDb still null for {series_name}, using Google Fallback.")
        final_imdb = f"https://www.imdb.com/find?q={series_name.replace(' ', '+')}"

    final_crunchyroll = jikan.get("crunchyroll")
    if not final_crunchyroll:
        print(f"Crunchyroll null for {series_name}, using Search Fallback.")
        final_crunchyroll = (
            f"https://www.crunchyroll.com/search?q={series_name.replace(' ', '+')}"
        )

    return {
        "about": jikan["about"],
        "poster": jikan["poster"],
        "release_year": jikan["release_year"],
        "genre": jikan["genre"],
        "imdb_link": final_imdb,
        "rt_link": tmdb["rt"],
        "crunchyroll": final_crunchyroll,
    }


def populate_movie_data(movie_name):
    jikan = fetch_jikan_anime(movie_name)
    if not jikan:
        return None

    tmdb = fetch_tmdb_links(movie_name, media_type="movie", year=jikan["release_year"])

    final_imdb = jikan.get("imdb_link") or tmdb.get("imdb")
    if not final_imdb:
        final_imdb = f"https://www.imdb.com/find?q={movie_name.replace(' ', '+')}"

    final_crunchyroll = jikan.get("crunchyroll")
    if not final_crunchyroll:
        final_crunchyroll = (
            f"https://www.crunchyroll.com/search?q={movie_name.replace(' ', '+')}"
        )

    return {
        "about": jikan["about"],
        "poster": jikan["poster"],
        "release_year": jikan["release_year"],
        "genre": jikan["genre"],
        "imdb_link": final_imdb,
        "rt_link": tmdb["rt"],
        "crunchyroll": final_crunchyroll,
    }


def get_obj_or_404(model, pk):
    """
    Generic reusable function to get object by PK or return proper Response.
    :param model: Django model class
    :param pk: primary key
    :return: tuple (object or None, error Response or None)
    """
    if pk is None:
        return None, Response(
            {"error": "Primary key is required"}, status=status.HTTP_400_BAD_REQUEST
        )
    try:
        obj = model.objects.get(pk=pk)
    except model.DoesNotExist:
        return None, Response(
            {"error": "Object not found"}, status=status.HTTP_404_NOT_FOUND
        )
    return obj, None