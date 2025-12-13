import os
import logging
import aiohttp
import asyncio
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

logger = logging.getLogger(__name__)
basic_info = ["title", "year", "genre", "rating", "description", "country", "poster"]


async def search_film_with_google_api(film_name: str):
    """
    Асинхронно выполняет поиск через Google Custom Search API.
    """
    api_key = os.getenv("GOOGLE_API_KEY")
    cx = os.getenv("GOOGLE_CX_ID")

    if not api_key or not cx:
        logger.error("Google API Key or CX ID is not set")
        return []

    try:
        service = build("customsearch", "v1", developerKey=api_key)

        res = (
            service.cse()
            .list(
                q=f"смотреть {film_name} онлайн бесплатно",
                cx=cx,
            )
            .execute()
        )

        results = []
        if "items" in res:
            for item in res["items"]:
                results.append(item)

        return results

    except Exception as e:
        logger.error(f"Error while searching with Google API: {e}")
        return []


async def check_url_availability(url: str) -> bool:

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=1) as response:
                return response.status == 200
    except Exception as e:
        logger.error(f"Error while checking URL {url}: {e}")
        return False


async def search_film_from_scrapping(
    film_name: str,
) -> tuple[tuple[list[list[dict]], list[str]], list[str]]:
    results = await search_film_with_google_api(film_name)

    if not results:
        logger.warning(f"No search results found for {film_name}")
        return ([[]], []), []

    save_res = True
    res = []
    links = []

    tasks = []
    for item in results:
        film_url = item.get("link")
        if film_url:
            tasks.append(check_url_availability(film_url))

    availability = await asyncio.gather(*tasks)

    for idx, item in enumerate(results):
        film_url = item.get("link")
        if (not film_url or not availability[idx]) and not idx == len(results) - 1:
            continue

        links.append(film_url)
        if save_res:
            save_res = False
            logger.info(f"Found available URL: {film_url}")
            pagemap = item.get("pagemap", {})
            movie = pagemap.get("movie", {})
            meta = pagemap.get("metatags", {})
            moviereview = pagemap.get("moviereview", {})

            if isinstance(movie, list):
                movie = movie[0] if len(movie) else {}
            if isinstance(meta, list):
                meta = meta[0] if len(meta) else {}
            if isinstance(moviereview, list):
                moviereview = moviereview[0] if len(moviereview) else {}

            res = [
                [
                    [
                        {
                            "title": item.get("title", "Неизвестно"),
                            "year": movie.get("datecreated", "Дата не известна"),
                            "genre": movie.get("genre", "Жанр неизвестен"),
                            "rating": moviereview.get(
                                "originalrating", "Рейтинг не известен"
                            ),
                            "description": item.get("snippet", "Описание недоступно")
                            + " "
                            + movie.get("description", ""),
                            "country": "Нет данных с сайта",
                            "poster": meta.get("og:image", None),
                            "extra_info": {
                                "webUrl": film_url,
                                "video": movie.get("video", None),
                                "actor": movie.get("actor", "Актеры не указаны"),
                                "typicalagerange": movie.get(
                                    "typicalagerange", "Возрастная категория не указана"
                                ),
                                "displayLink": item.get("displayLink", ""),
                                "htmlFormattedUrl": item.get("htmlFormattedUrl", ""),
                            },
                        }
                    ]
                ],
                [[item.get("displayLink") if item.get("displayLink") else film_url]],
            ]

    if save_res:
        logger.warning("No available links found.")
        return ([[]], []), []

    return res, links
