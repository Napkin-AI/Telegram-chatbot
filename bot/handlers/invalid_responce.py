from aiogram import types, Router

router = Router()

@router.message()
async def invalid_response_handler(message: types.Message):
    await message.answer(
        "Это заглушка! Извини, я не понимаю эту команду. Напиши /help, чтобы увидеть доступные команды.\n"
        "Возможно, эта команда не проиписана в ТЗ для БДЗ, а, возможно, я просто не увидел\n"
        "Напиши пожайлуста, если я что-то сделал не так (если это критически важно для получения балла Больших домашек)"
        )
