import aiohttp
import asyncio
import logging
import os

from aiogram import types, Router
from dotenv import load_dotenv

from bot.domain.storage import Storage

load_dotenv()

# globals
logger = logging.getLogger(__name__)
router = Router()
basic_info = ["title", "year", "genre", "rating", "description", "country", 'poster']

# Helpers to search films
async def search_film_omdb(session: aiohttp.ClientSession, film_name: str) -> list[dict]:
    """
    Seach film information using OMDB API.
    """
    api_key = os.getenv("OMDB_API_KEY")

    if api_key is None:
        logger.info("OMDB_API_KEY is not set")
        return []

    logger.info("OMDB_API_KEY was found")

    base_url = f"https://www.omdbapi.com/?apikey={api_key}&t={film_name}"

    try:
        async with session.get(base_url) as response:
            if response.status == 200:
                data = await response.json()
                logger.info(data)
                if data.get("Response") == "True":
                    local_info = ["Title", "Year", "Genre", "imdbRating", "Plot", "Country", 'Poster']
                    result = {
                        basic_cat: data[local_cat] for basic_cat, local_cat in zip(basic_info, local_info)
                    }
                    result['extra_info'] = { key: data[key] for key in data.keys() if key not in local_info }
                    return [result]
                else:
                    logger.warning(f"Film not found: {film_name}")
                    return [{}]
            else:
                logger.info(f"OMDB API request failed with status {response.status}")
                return [{}]

    except Exception as e:
        logger.error(f"Error while fetching data from OMDB API: {e}")
        return [{}]

async def _search_film_kinopoisk_by_keyword(session: aiohttp.ClientSession, base_url: str, headers: dict, params: dict) -> dict:

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

async def _search_film_kinopoisk_by_id(session: aiohttp.ClientSession, base_url: str, headers: dict, kinopoisk_id: int) -> dict:

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

async def search_film_kinopoisk(session: aiohttp.ClientSession, film_name: str) -> list[dict]:
    """
    Seach film information using OMDB API.
    """
    api_key = os.getenv("KINOPOISK_API_KEY")

    if api_key is None:
        logger.info("KINOPOISK_API_KEY is not set")
        return []

    logger.info("KINOPOISK_API_KEY was found")

    base_url = "https://kinopoiskapiunofficial.tech/api/v2.2/films"

    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json"
    }
    params = {
        "keyword": film_name
    }

    try:
        all_variants = await _search_film_kinopoisk_by_keyword(session, base_url, headers, params)

        if all_variants.get("items") is None or not len(all_variants["items"]):
            return []

        kinopoisk_ids = [item.get("kinopoiskId") for item in all_variants["items"][:2]]

        tasks = [_search_film_kinopoisk_by_id(session, base_url, headers, kinopoisk_id) for kinopoisk_id in kinopoisk_ids]
        films_data = await asyncio.gather(*tasks)

        local_info = ["nameOriginal", "year", "genres", "ratingImdb", "description", "countries", "posterUrl"]
        result = []

        for film in films_data:
            film_result = {
                basic_cat: film[local_cat] for basic_cat, local_cat in zip(basic_info, local_info)
            }
            film_result["extra_info"] = { key: film.get(key) for key in film.keys() if key not in local_info }
            result.append(film_result)

        return result

    except Exception as e:
        logger.error(f"Error while fetching data from kinopoisk API: {e}")
        return []

async def search_film(film_name: str) -> list[dict]:

    async with aiohttp.ClientSession() as session:
        resourses = [
            search_film_kinopoisk(session, film_name),
            search_film_omdb(session, film_name)
        ]
        results = await asyncio.gather(*resourses)
        sources = [
            "Open movie database (OMDb), https://www.omdbapi.com/",
            "Kinoposk, https://www.kinopoisk.ru/"
        ]
        return results, sources

async def parse_response(response: list[list[dict]]) -> list[tuple[str, str | None, int]]:
    result = []

    for source_idx, source_variants in enumerate(response):
        source_count = 0
        for film in source_variants[:2]:
            if not film:
                continue

            title = film.get("title", "Неизвестно")
            year = film.get("year", "Неизвестен")
            genre = film.get("genre", "Жанр не указан")
            rating = film.get("rating", "Рейтинг не указан")
            description = film.get("description", "Описание не доступно")
            country = film.get("country", "Страна не указана")
            poster_url = film.get("poster", None)

            if not title:
                if film['extra_info'].get('nameRu'):
                    title = film['extra_info']['nameRu']
                elif film['extra_info'].get('nameEn'):
                    title = film['extra_info']['nameEn']

            if isinstance(genre, list):
                if len(genre) == 0:
                    genre = "Жанр не указан"
                else:
                    genre = ', '.join([str(genre[idx]['genre']) for idx in range(len(genre)) if genre[idx]['genre']])

            if isinstance(country, list):
                if len(genre) == 0:
                    country = "Страна не указана"
                else:
                    country = ', '.join([str(country[idx]['country']) for idx in range(len(country)) if country[idx]['country']])

            film_url = film["extra_info"].get("webUrl")
            if not film_url:
                film_url = film["extra_info"].get("Website")

            film_info = f"Название: {title}\nГод: {year}\nЖанр: {genre}\nРейтинг: {rating}\nОписание: {description}\nСтрана: {country}\n URL: {"Unavailable" if film_url is None else film_url}\n"

            result.append((film_info, poster_url, source_idx))

            source_count += 1
            if source_count >= 2:
                break

    return result

async def process_film_name(film_name: str):

    return

@router.message()
async def find_film_handler(message: types.Message, psql_storage: Storage):
    film_name = await process_film_name(message.text.strip())
    user_id = message.from_user.id

    results, sources = await search_film(film_name)

    await psql_storage.save_user_query(user_id, film_name)

    output = await parse_response(results)
    if len(output) == 0:
        await message.answer("К сожалению, такого фильма нет в наших базах!:(\nПопробуй ввести его без ошибок.\n")
        return

    for out_text, poster_url, source_idx in output:

        await message.answer(f"Посмотрим, что удалось найти на ресурсе {sources[source_idx]}\n" + out_text)
        if poster_url:
            try:
                await message.answer_photo(poster_url)
            except Exception as e:
                await message.answer("Постер не доступен на сайте! Воможно, он был удален.")
