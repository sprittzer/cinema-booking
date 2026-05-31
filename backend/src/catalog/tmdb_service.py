from typing import Any

import httpx

from src.common.config import config

TMDB_GENRE_MAP = {
    28: "action",
    18: "drama",
    35: "comedy",
    27: "horror",
    878: "sci_fi",
    53: "thriller",
    10749: "romance",
    16: "animation",
    99: "documentary",
}


# TMDB v3 base, всегда с /3 в конце, без лишних слэшей
def _base() -> str:
    raw = config.tmdb_base_url.rstrip("/")
    return raw if raw.endswith("/3") else f"{raw}/3"


def _client() -> httpx.AsyncClient:
    return httpx.AsyncClient(
        headers={"Authorization": f"Bearer {config.tmdb_api_key}"},
        timeout=10.0,
    )


async def search_movies(query: str) -> list[dict[str, Any]]:
    async with _client() as client:
        response = await client.get(
            f"{_base()}/search/movie",
            params={"query": query, "language": "ru-RU"},
        )
        response.raise_for_status()
        results = response.json().get("results", [])
        return [
            {
                "tmdb_id": r["id"],
                "title": r.get("title") or r.get("original_title", ""),
                "year": (r.get("release_date") or "")[:4] or None,
                "poster_url": f"https://image.tmdb.org/t/p/w200{r['poster_path']}" if r.get("poster_path") else None,
            }
            for r in results[:10]
        ]


async def fetch_movie(tmdb_id: int) -> dict[str, Any]:
    async with _client() as client:
        response = await client.get(
            f"{_base()}/movie/{tmdb_id}",
            params={"language": "ru-RU"},
        )
        response.raise_for_status()
        return response.json()  # type: ignore[no-any-return]


async def fetch_trailer_url(tmdb_id: int) -> str | None:
    async with _client() as client:
        response = await client.get(f"{_base()}/movie/{tmdb_id}/videos")
        response.raise_for_status()
        videos = response.json().get("results", [])
        trailer = next(
            (v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"),
            None,
        )
        if trailer:
            return f"https://www.youtube.com/watch?v={trailer['key']}"
        return None


async def fetch_images(tmdb_id: int) -> list[str]:
    async with _client() as client:
        response = await client.get(f"{_base()}/movie/{tmdb_id}/images")
        response.raise_for_status()
        backdrops = response.json().get("backdrops", [])
        return [f"https://image.tmdb.org/t/p/w1280{b['file_path']}" for b in backdrops[:10] if b.get("file_path")]


_US_CERT_MAP = {"G": "0+", "PG": "6+", "PG-13": "12+", "R": "16+", "NC-17": "18+"}


async def fetch_age_rating(tmdb_id: int) -> str | None:
    async with _client() as client:
        response = await client.get(f"{_base()}/movie/{tmdb_id}/release_dates")
        response.raise_for_status()
        results = response.json().get("results", [])

    by_country = {r["iso_3166_1"]: r["release_dates"] for r in results}

    for country in ("RU", "US"):
        for rd in by_country.get(country, []):
            cert = rd.get("certification", "").strip()
            if cert:
                return str(_US_CERT_MAP.get(cert, cert)) if country == "US" else str(cert)

    return None


async def fetch_person(person_id: int) -> dict[str, Any]:
    async with _client() as client:
        response = await client.get(f"{_base()}/person/{person_id}", params={"language": "ru-RU"})
        if response.status_code != 200:
            return {}
        return response.json()  # type: ignore[no-any-return]


async def fetch_credits(tmdb_id: int) -> list[dict[str, Any]]:
    async with _client() as client:
        response = await client.get(f"{_base()}/movie/{tmdb_id}/credits", params={"language": "ru-RU"})
        response.raise_for_status()
        cast = response.json().get("cast", [])
    return [
        {
            "tmdb_id": p["id"],
            "name": p.get("name", ""),
            "character": p.get("character") or None,
            "photo_url": f"https://image.tmdb.org/t/p/w185{p['profile_path']}" if p.get("profile_path") else None,
        }
        for p in sorted(cast, key=lambda x: x.get("order", 999))[:10]
    ]


def map_genre(genre_ids: list[int]) -> str:
    for gid in genre_ids:
        if gid in TMDB_GENRE_MAP:
            return TMDB_GENRE_MAP[gid]
    return "other"
