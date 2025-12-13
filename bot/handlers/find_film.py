import asyncio
import logging

from aiogram import types, Router
from bot.handlers.search_engine._find_film_in_google import search_film_from_scrapping
from bot.handlers.search_engine._find_film_using_api import search_film_from_api
from bot.domain.storage import Storage

# globals
logger = logging.getLogger(__name__)
router = Router()
basic_info = ["title", "year", "genre", "rating", "description", "country", 'poster']

async def parse_response(response: list[list[dict]]) -> list[tuple[str, str | None, int]]:
    result = []
    for source_idx, source_variants in enumerate(response):
        if len(source_variants) == 0:
            continue

        for film in source_variants:
            if not film:
                continue

            title = film.get("title", "Неизвестно")
            year = film.get("year", "Неизвестен")

            if isinstance(film.get("genre"), str):
                genre = film["genre"]
            else:
                genre = ', '.join([str(g) for g in film.get("genre", ["Жанр не указан"])])

            if isinstance(film.get("country"), str):
                country = film["country"]
            else:
                country = ', '.join([str(g) for g in film.get("country", ["Страна не указана"])])

            rating = film.get("rating", "Рейтинг не указан")
            description = film.get("description", "Описание не доступно")
            poster_url = film.get("poster", None)

            film_url = film["extra_info"].get("webUrl") or film["extra_info"].get("Website") or "Unavailable"
            film_info = f"Название: {title}\nГод: {year}\nЖанр: {genre}\nРейтинг: {rating}\nОписание: {description}\nСтрана: {country}\n URL: {film_url}"

            result.append((film_info, poster_url, source_idx))
            break

    return result

async def get_answer(message: types.Message, output: list[tuple[str, str | None, int]], sources: list[str]) -> None:
    for out_text, poster_url, source_idx in output:
        await message.answer(f"Посмотрим, что удалось найти на ресурсе {sources[source_idx]}\n" + out_text)
        if poster_url:
            try:
                await message.answer_photo(poster_url)
            except Exception:
                await message.answer("Постер не доступен на сайте! Возможно, он был удален.")


async def responce_links(message: types.Message, links: list[str]) -> None:
    await message.answer("Вот список всех доступных сайтов с похожими фильмами. Иногда для входа нужен VPN\n")
    await message.answer('\n'.join(links))

@router.message()
async def find_film_handler(message: types.Message, psql_storage: Storage):
    film_name = message.text.strip()
    user_id = message.from_user.id

    await psql_storage.save_user_query(user_id, film_name)

    api_results, api_sources = await search_film_from_api(film_name)
    (search_result, search_sources), links = await search_film_from_scrapping(film_name)

    api_output = await parse_response(api_results)
    scrapping_output = await parse_response(search_result)

    if not api_output and not scrapping_output:
        await message.answer("К сожалению, такого фильма нет в наших базах!:(\nПопробуй ввести его без ошибок.\n")
        return

    if api_output:
        await message.answer("Информация, которую удалось найти при использовании API баз данных: ")
        await get_answer(message, api_output, api_sources)

    if scrapping_output:
        await message.answer("Информация, которую удалось найти при скрапинге поиска: ")
        await get_answer(message, scrapping_output, search_sources)
        if len(links) > 1:
            await responce_links(message, links)

