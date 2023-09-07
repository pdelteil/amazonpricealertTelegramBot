# amazonpricealertTelegramBot
Python program to watch price changes for Amazon products. It displays updates in a Telegram bot. The user can add/remove watched items using only the bot

# How to use

## Telegram
1. Create a Telegram Bot ([More details](https://medium.com/@ManHay_Hong/how-to-create-a-telegram-bot-and-send-messages-with-python-4cf314d9fa3e))
2. Create a group and add the bot to it. 
3. Make this request:
   ` curl https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates`

From here you will get the CHAT_ID. If it doesn't work, take a look [here.](https://stackoverflow.com/questions/32423837/telegram-bot-how-to-get-a-group-chat-id)

5. Add both previous tokens to the file `config.ini.example` and save it as `config.ini`

## Python
1. clone this repo

   `git clone https://github.com/pdelteil/amazonpricealertTelegramBot.git`
2. Install python modules

   `pip -r requirements.txt`

3.  Run it doing
   
       `python amazon.price.alert.py & python actions.bot.py` 

## Using the bot 
1. /add_item: Add an item to the watch list.
 
   Syntax: **/add_item NAME FOR THE ITEM, URL**
   
![image](https://github.com/pdelteil/amazonpricealertTelegramBot/assets/20244863/b7184151-9a31-4a58-896e-dc11ec002ef7)

   
2. read_items

   ![image](https://github.com/pdelteil/amazonpricealertTelegramBot/assets/20244863/8febd8da-e745-4441-ac4c-dc2782fde773)

3. /remove_item: Removes an item from the watch list.

   Syntax: /remove_item **id**

   ![image](https://github.com/pdelteil/amazonpricealertTelegramBot/assets/20244863/caf7a50e-c8a7-427b-9de8-548e59f0a97a)

## Supported ecommerce sites
- Amazon
- Suarez Store (https://www.suarezclothing.com/)
- Cyclewear (https://cyclewear.com.co)   
- Bikeexchange (https://www.bikeexchange.com.co)
- Bikehouse (https://www.bikehouse.co)
