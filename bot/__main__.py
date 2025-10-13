import time

import bot.database_client
import bot.telegram_client

def main() -> None:
    offset: int = 0
    
    try:
        while True:
            updates = bot.telegram_client.getUpdates(offset)
            bot.database_client.persist_updates(updates)
            
            for update in updates:
                
                if 'message' not in update: 
                    bot.telegram_client.sendMessage(
                        chat_id=update['message']['chat']['id'],
                        text='Something is wrong. Try again'
                    )
                    continue
                
                if 'text' in update['message']:
                    bot.telegram_client.sendMessage(
                        chat_id=update['message']['chat']['id'],
                        text=update['message']['text']
                    )
                elif 'sticker' in update['message']:
                    sticker_file_id = update['message']['sticker']['file_id']
                    bot.telegram_client.sendSticker(
                        chat_id=update['message']['chat']['id'],
                        sticker=sticker_file_id
                    )
                else:
                    bot.telegram_client.sendMessage(
                        chat_id=update['message']['chat']['id'],
                        text="Not implemented"
                    )

                offset = max(offset, update['update_id'] + 1)
                    
            time.sleep(1)
        
    except KeyboardInterrupt:
        print("Done")


if __name__ == '__main__':
    main()