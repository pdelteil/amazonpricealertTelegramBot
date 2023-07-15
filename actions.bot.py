import logging
import configparser
from telegram import __version__ as TG_VER

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
from telegram import ForceReply, Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def get_last_item(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
        line_count = len(lines)
        last_line = lines[-1]
        parts = last_line.split('=')
        if len(parts) > 1:
            id = parts[0].strip()
            return id
        else:
            return 0

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hi {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

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

async def remove_items_by_id(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = configparser.ConfigParser()
    config.read(PRODUCTS_FILE)
    line = update.message.text  # Get the line from the chat input
    number = line.replace("/remove_item ", "")
    print(number)

    if config.has_option('PRODUCTS', str(number)):
        config.remove_option('PRODUCTS', str(number))
        with open(PRODUCTS_FILE, 'w') as file:
            config.write(file)
        await update.message.reply_text(f"Item {number} removed successfully.")
    else:
        await update.message.reply_text(f"Item {number} not found in {PRODUCTS_FILE} file.")
    # Update the IDs of the following items
    products = config.items('PRODUCTS')
    updated_config = configparser.ConfigParser()
    updated_config['PRODUCTS'] = {}
    for i, (id, info) in enumerate(products, start=1):
        updated_config['PRODUCTS'][str(i)] = info

    with open(PRODUCTS_FILE, 'w') as file:
        updated_config.write(file)

async def read_items(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    config = configparser.ConfigParser()
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
    line = line.replace("/add_item ", "") 
    id = get_last_item(PRODUCTS_FILE)
    parts = line.split(',', 1)

    if len(parts) > 1:
        line = parts[0] + ',$0,' + parts[1]
    try:
        number = int(id) +1 

    except ValueError:
        return None
    line = str(number) + " = " + line
    with open(PRODUCTS_FILE, 'a') as file:
        file.write(line)
    await update.message.reply_text('Item added successfully.')

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

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
