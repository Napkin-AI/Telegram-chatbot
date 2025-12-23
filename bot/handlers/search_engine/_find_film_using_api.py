import aiohttp
import asyncio
import logging
import os

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)
basic_info = ["title", "year", "genre", "rating", "description", "country", "poster"]


async def search_film_omdb(
    session: aiohttp.ClientSession, film_name: str
) -> tuple[list[dict], str]:
    """
    Seach film information using OMDB API.
    """
    api_key = os.getenv("OMDB_API_KEY")

    if api_key is None:
        logger.info("OMDB_API_KEY is not set")
        return [{}], ''

    logger.info("OMDB_API_KEY was found")

    base_url = f"https://www.omdbapi.com/?apikey={api_key}&t={film_name}"

    try:
        async with session.get(base_url) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(data)
                if data.get("Response") == "True":
                    local_info = [
                        "Title",
                        "Year",
                        "Genre",
                        "imdbRating",
                        "Plot",
                        "Country",
                        "Poster",
                    ]
                    result = {
                        basic_cat: data[local_cat]
                        for basic_cat, local_cat in zip(basic_info, local_info)
                    }
                    if isinstance(data["Genre"], list) and len(data["Genre"]):
                        result["genre"] = ", ".join(data["Genre"])
                    result["extra_info"] = {
                        key: data[key] for key in data.keys() if key not in local_info
                    }
                    return [
                        result
                    ], "Open movie database (OMDb), https://www.omdbapi.com/"
                else:
                    logger.warning(f"Film not found: {film_name}")
                    return [{}], ''
            else:
                logger.info(f"OMDB API request failed with status {response.status}")
                return [{}], ''

    except Exception as e:
        logger.error(f"Error while fetching data from OMDB API: {e}")
        return [{}], ''


async def _search_film_kinopoisk_by_keyword(
    session: aiohttp.ClientSession, base_url: str, headers: dict, params: dict
) -> dict:

    async with session.get(base_url, headers=headers, params=params) as response:
        if response.status == 200:
            data = await response.json()
            logger.info(data)
            if data.get("total", 0) == 0:
                logger.warning(f"Film not found: {params.get('keyword')}")
                return {}
        else:
            logger.info(f"kinopoisk API request failed with status {response.status}")
            return {}

    return data


async def _search_film_kinopoisk_by_id(
    session: aiohttp.ClientSession, base_url: str, headers: dict, kinopoisk_id: int
) -> dict:

    if kinopoisk_id is None:
        return {}

    async with session.get(base_url + f"/{kinopoisk_id}", headers=headers) as response:
        if response.status == 200:
            data = await response.json()
            logger.info(data)
            if not data or not len(data):
                return {}
        else:
            logger.info(f"kinopoisk API request failed with status {response.status}")
            return {}

    return data


async def search_film_kinopoisk(
    session: aiohttp.ClientSession, film_name: str
) -> tuple[list[dict], str]:
    """
    Seach film information using OMDB API.
    """
    api_key = os.getenv("KINOPOISK_API_KEY")

    if api_key is None:
        logger.info("KINOPOISK_API_KEY is not set")
        return [], ''

    logger.info("KINOPOISK_API_KEY was found")

    base_url = "https://kinopoiskapiunofficial.tech/api/v2.2/films"

    headers = {"X-API-KEY": api_key, "Content-Type": "application/json"}
    params = {"keyword": film_name}

    try:
        all_variants = await _search_film_kinopoisk_by_keyword(
            session, base_url, headers, params
        )

        if all_variants.get("items") is None or not len(all_variants["items"]):
            return [], ""

        kinopoisk_ids = [item.get("kinopoiskId") for item in all_variants["items"][:2]]

        tasks = [
            _search_film_kinopoisk_by_id(session, base_url, headers, kinopoisk_id)
            for kinopoisk_id in kinopoisk_ids
        ]
        films_data = await asyncio.gather(*tasks)

        local_info = [
            "nameOriginal",
            "year",
            "genres",
            "ratingImdb",
            "description",
            "countries",
            "posterUrl",
        ]
        result = []

        for film in films_data:
            film_result = {
                basic_cat: film[local_cat]
                for basic_cat, local_cat in zip(basic_info, local_info)
            }
            if isinstance(film_result["genre"], list):
                film_result["genre"] = ", ".join(
                    [genre["genre"] for genre in film_result["genre"]]
                )
            if isinstance(film_result["country"], list):
                film_result["country"] = ", ".join(
                    [country["country"] for country in film_result["country"]]
                )
            film_result["extra_info"] = {
                key: film.get(key) for key in film.keys() if key not in local_info
            }
            result.append(film_result)

        return result, "Kinoposk, https://www.kinopoisk.ru/"

    except Exception as e:
        logger.error(f"Error while fetching data from kinopoisk API: {e}")
        return [], ""


async def search_film_from_api(film_name: str) -> tuple[list[list[dict]], list[str]]:

    async with aiohttp.ClientSession() as session:
        resourses = [
            search_film_kinopoisk(session, film_name),
            search_film_omdb(session, film_name),
        ]
        res = await asyncio.gather(*resourses)

        results, sources = [], []
        for item in res:
            if len(item) != 2 or not item[1]:
                continue
            data, source = item
            results.append(data)
            sources.append(source)

        return results, sources
