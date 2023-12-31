import configparser
from telegram import __version__ as TG_VER
from urllib.parse import urlparse
from telegram import ForceReply, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackQueryHandler

PRODUCTS_FILE= 'products.ini'
CONFIG_FILE = 'config.ini'

# Read params from config file
config = configparser.ConfigParser()
config.read(CONFIG_FILE)

TELEGRAM_TOKEN = config.get('TELEGRAM', 'TELEGRAM_TOKEN')
CHAT_ID = config.get('TELEGRAM', 'CHAT_ID')
apiURL = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'

# Global variable to store user input
user_input = {}
try:
    from telegram import __version_info__
except ImportError:
    __version_info__ = (0, 0, 0, 0, 0)  # type: ignore[assignment]

if __version_info__ < (20, 0, 0, "alpha", 1):
    raise RuntimeError(
        f"This example is not compatible with your current PTB version {TG_VER}. To view the "
        f"{TG_VER} version of this example, "
        f"visit https://docs.python-telegram-bot.org/en/v{TG_VER}/examples.html")

def validate_input(input):
     # Check if the input string is empty
    if not input:
        return False

    # Check if the input string starts with '/add_item'
    if not input.startswith("/add_item"):
        return False

    # Find the index of the comma
    comma_index = input.find(',')

    if comma_index == -1:
        url_part = input[len("/add_item"):].strip()
        return is_valid_url(url_part)

    # Check if the comma exists and is not the last character
    if comma_index == len(input) - 1:
        return False

    return True

def read_value(input):
    # Find the index of the comma
    comma_index = input.find(',')

    # If comma_index is -1, the input string is only '/add_item URL'
    if comma_index == -1:
        url_part = input[len("/add_item"):].strip()
        return "", url_part

    # Extract the string part and URL part
    string_part = input[len("/add_item"):comma_index].strip()
    url_part = input[comma_index + 1:].strip()

    return string_part, url_part

def is_valid_url(url):
    # Parse the URL and check if it has a valid scheme and netloc
    parsed_url = urlparse(url)
    if parsed_url.scheme and parsed_url.netloc:
        return True
    return False

def get_last_item(file_path):
    with open(file_path, 'r') as file:
        lines = [line.rstrip('\n') for line in file.readlines() if line.strip()]
        last_line = lines[-1]
        print(last_line)
        parts = last_line.split(' = ')
        if len(parts) > 1:
            id = parts[0].strip()
            return id
        else:
            return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(main_menu_message(),
                         reply_markup=main_menu_keyboard())
    """Send a message when the command /start is issued."""
    #user = update.effective_user
    #await update.message.reply_html(
   #     rf"Hi {user.mention_html()}!",
    #    reply_markup=ForceReply(selective=True),
    #)


def first_menu(bot, update):
    bot.callback_query.message.edit_text(first_menu_message(), reply_markup=first_menu_keyboard())
    # update.message.reply_html(
    #    rf"Menu1!",
    #    reply_markup=ForceReply(selective=True),
    #)


def main_menu(bot, update):
  bot.callback_query.message.edit_text(main_menu_message(),
                          reply_markup=main_menu_keyboard())

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    help_message = """
    Welcome to my bot! Here are the available commands:
    /start - Start the bot
    /help - Get help and instructions
    /read_items - Show all watched items 
    /add_item NAME, URL - add item to the list 
    /remove_item ID - remove item by its id
    """
    await update.message.reply_text(help_message)

def remove_after_number(input):
    # Split the input string by whitespace
    parts = input.split()

    # Check if the input string has enough parts
    if len(parts) < 2:
        return input

    # Extract the number part
    number_part = parts[1]

    # Check if the number part is numeric
    if not number_part.isdigit():
        return input

    # Join the first two parts and return the result
    result = ' '.join(parts[:2])
    return result

async def remove_items_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = configparser.RawConfigParser()
    config.read(PRODUCTS_FILE)
    line = update.message.text  # Get the line from the chat input
    parts = line.strip().split()

    # Check if the input has two parts and the first part is "/remove_item"
    if len(parts) == 2 and parts[0] == "/remove_item":
        # Check if the second part (ID) is an integer
        try:
            id = int(parts[1])
        except ValueError:
            return await update.message.reply_text(f"wrong format, id not an int")

        # ID is on the products file
        if config.has_option('PRODUCTS', str(id)):
            config.remove_option('PRODUCTS', str(id))
            with open(PRODUCTS_FILE, 'w') as file:
                config.write(file)
            # Update the IDs of the following items
            products = config.items('PRODUCTS')
            updated_config = configparser.RawConfigParser()
            updated_config['PRODUCTS'] = {}
            for i, (id_, info) in enumerate(products, start=1):
                updated_config['PRODUCTS'][str(i)] = info
    
            with open(PRODUCTS_FILE, 'w') as file:
                updated_config.write(file)

            return await update.message.reply_text(f"Item {id} removed successfully.")
        else:
            await update.message.reply_text(f"Item {id} not found in {PRODUCTS_FILE} file.")
    else:
        return await update.message.reply_text(f"wrong format") 

async def read_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    #config = configparser.ConfigParser()
    config = configparser.RawConfigParser()
    config.read(PRODUCTS_FILE)
    message_content = ""

    if config.has_section('PRODUCTS'):
        products = config.items('PRODUCTS')
        for number, info in products:
            message_content += f"Item {number}: {info}\n"

    if message_content:
        await update.message.reply_text(message_content)
    else:
        await update.message.reply_text(f"No items found in the {PRODUCTS_FILE} file.")

# Handler function for adding a line to the file
async def add_item(update, context):
    line = update.message.text  # Get the line from the chat input

    if not validate_input(line):
        print("Input is not in the required form.")
        await update.message.reply_text(f"Input is not in the required form.")
    else:
        name, url = read_value(line) 
        id = get_last_item(PRODUCTS_FILE)
        print("id",id)

        line = name + ',$0,' + url
        print(line)
        try:
            number = int(id) +1 

        except ValueError:
            return None
        new_line = str(number) + " = " + line + "\n"

        # Read the content of the file
        with open(PRODUCTS_FILE, 'r') as file:
            lines = file.readlines()
        modified_lines = [lines[0]]
        for line in lines:
            if line.strip() and ("," in line or "=" in line):
                modified_lines.append(line)
        modified_lines.append(new_line)
        # Write the modified lines back to the file
        with open(PRODUCTS_FILE, 'w') as file:
            file.writelines(modified_lines)
        await update.message.reply_text('Item added successfully.')

def main_menu_keyboard():
  keyboard = [[InlineKeyboardButton('/read_items', callback_data='m1')],
              [InlineKeyboardButton('Menu 2', callback_data='m2')],
              [InlineKeyboardButton('Menu 3', callback_data='m3')]]
  return InlineKeyboardMarkup(keyboard)

def main_menu_message():
  return 'Choose the option in main menu:'

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("read_items", read_items))
    application.add_handler(CommandHandler("add_item", add_item))
    application.add_handler(CommandHandler("read_items",read_items))
    application.add_handler(CommandHandler("remove_item",remove_items_by_id))

    application.add_handler(CallbackQueryHandler(main_menu, pattern='main'))
    application.add_handler(CallbackQueryHandler(first_menu, pattern='m1'))
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

