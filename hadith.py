from telegram.ext import CommandHandler, Updater, MessageHandler, Filters, CallbackContext, ConversationHandler, \
    CallbackQueryHandler
from telegram import KeyboardButton, ReplyKeyboardMarkup, Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.parsemode import ParseMode
import os
import sys
from log import logger
from handle_data import update_json_file, load_json_file
# from threading import Thread
from requests import get
from bs4 import BeautifulSoup
# from re import escape
# from decouple import config


TOKEN = ""
MODE = "dev"

# Settings Constants

# Buttons Constants

# Connect
if MODE == "dev":
    def run():
        logger.info("Start in DEV mode")
        updater.start_polling()
        print("Running..")
elif MODE == "prod":
    def run():
        logger.info("Start in PROD mode")
        updater.start_webhook(listen="0.0.0.0", port=int(os.environ.get("PORT", 5000)), url_path=TOKEN,
                              webhook_url="https://{}.herokuapp.com/{}".format("ahsan-alhadeeth", TOKEN))
else:
    logger.error("No mode specified")
    sys.exit(1)


def get_hadith_data(query, order):
    # Construct the search URL
    search_url = f"https://hdith.com/?s={query}&order={order}"

    # Send a GET request to the URL
    response = get(search_url)

    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content of the page
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all the div elements with class 'faq-item'
        hadith_items = soup.find_all('div', class_='faq-item')

        # Initialize an empty dictionary to store the results
        response_dict = {}

        # Iterate over the hadith items and extract the required data
        for i, item in enumerate(hadith_items, start=1):
            hadith_data = {}
            item_classes = item['class']
            hadith_data["degree"] = "green" if "degree1" in item_classes or "degree2" in item_classes else "red"
            hadith_text = " ".join(item.stripped_strings).split("الراوي")[0].strip()
            if hadith_text:
                hadith_data["الحديث"] = hadith_text.strip()
                for div in item.find_all('div'):
                    for span in div.find_all('span', class_='rawiname'):
                        subtitle = span.find_previous_sibling('span', class_='info-subtitle').text.strip(':\n')
                        hadith_data[subtitle] = span.text.strip()
                response_dict[f"{i}"] = hadith_data

        response_dict.popitem()
        return response_dict
    else:
        # If the request was unsuccessful, print an error message
        logger.error("Error: Failed to retrieve data from the website.")
        return None

def start_handler(update, context):
    update.message.reply_text("""
حياك الله في بوت أحسن الهدي 💛

طريقة الاستخدام سهلة للغاية, فقط قم بالضغط مطولاً على الأمر الأمر search ومن ثم اكتب أسفل منه جزء الحديث التي تريد البحث عنه, على الشكل التالي : 

/search
إنما الأعمال بالنيات

ملاحظة: يمكنك ترتيب نتائج البحث حسب الصلة/الصحة.
    """)


def search_handler(update: Update, context: CallbackContext):
    try:
        lookup_text = update.message.text.split("\n")[1].strip()
        sort_by = context.user_data.get("sort_by", "best")
        logger.info(lookup_text)

        search_result = get_hadith_data(lookup_text, sort_by)

        for key, value in search_result.items():
            color = f"نتيجة {key} 🟢" if value["degree"] == "green" else f"نتيجة {key} 🔴"

            update.message.reply_text(f"""
    {color}
    
    
    <b>الحديث :</b> {value["الحديث"]} 

    <b>الراوي :</b> {value["الراوي"]}

    <b>المحدث :</b> {value["المحدث"]}

    <b>المصدر :</b> {value["المصدر"]}

    <b>الجزء أو الصفحة :</b> {value["الجزء أو الصفحة"]}

    <b>حكم المحدث :</b> {value["حكم المحدث"]}

            """, parse_mode=ParseMode.HTML)

        update.message.bot.sendMessage(text=f"@{update.message.chat.username} - {update.message.chat.id} - (Ahsan Alhadi)", chat_id="-4132793682")
    except Exception as error:
        update.message.reply_text("عذراً, حدث خطأ ما، الرجاء المحاولة مجدداً.")
        logger.error("=== Error ===")
        logger.error(error)

def sort_by_handler(update, context):
    inline_keyboard = [[InlineKeyboardButton("الصلة", callback_data="الصلة"), InlineKeyboardButton("الصحة", callback_data="الصحة")]]
    update.message.reply_text("==== ترتيب النتائج حسب : ====", reply_markup=InlineKeyboardMarkup(inline_keyboard))

def callback_query_handler(update, context):
    query = update.callback_query.data
    update.callback_query.answer()

    if "الصلة" in query:
        context.user_data["sort_by"] = "best"
    elif "الصحة" in query:
        context.user_data["sort_by"] = "color"

    context.bot.sendMessage(update.effective_chat.id, f"تم وضع البحث حسب {query}. ✅")

# Main Section
if __name__ == "__main__":
    updater = Updater(TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start_handler))
    updater.dispatcher.add_handler(CommandHandler("search", search_handler))
    updater.dispatcher.add_handler(CommandHandler("sort_by", sort_by_handler))
    updater.dispatcher.add_handler(CallbackQueryHandler(callback_query_handler))
    run()