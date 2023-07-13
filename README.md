# amazonpricealertTelegramBot
Python program to watch price changes for Amazon products. It displays updates in a Telegram bot. The user can add/remove watched items using only the bot

# How to use

1. Create a Telegram Bot ([More details](https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e))
2. Add the bot to a group
3. Make this request:
   ` curl https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates`

From here you will get the CHAT_ID. If it doesn't work, take a look [here.](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)

5. Add both previous tokens to the file `config.ini.example` and save it as `config.ini`
6. 
7. 
