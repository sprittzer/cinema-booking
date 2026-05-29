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


async def fetch_movie(tmdb_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.tmdb_base_url}/movie/{tmdb_id}",
            params={"api_key": config.tmdb_api_key, "language": "ru-RU"},
        )
        response.raise_for_status()
        return response.json()


async def fetch_trailer_url(tmdb_id: int) -> str | None:
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{config.tmdb_base_url}/movie/{tmdb_id}/videos",
            params={"api_key": config.tmdb_api_key},
        )
        response.raise_for_status()
        videos = response.json().get("results", [])
        trailer = next(
            (v for v in videos if v["type"] == "Trailer" and v["site"] == "YouTube"),
            None,
        )
        if trailer:
            return f"https://www.youtube.com/watch?v={trailer['key']}"
        return None


def map_genre(genre_ids: list[int]) -> str:
    for gid in genre_ids:
        if gid in TMDB_GENRE_MAP:
            return TMDB_GENRE_MAP[gid]
    return "other"
