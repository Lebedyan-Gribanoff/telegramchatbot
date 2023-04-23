import datetime
import logging
import sqlite3
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup

TOKEN = '6034472814:AAGQMRiI97yXXlIlok6yC0K08eCZTSILFf0'

reply_keyboard = [['/new_task', '/show_tasks'],
                  ['/delete_tasks', '/delete_all_tasks']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

# создаем дб где будем хранить список задач
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              task TEXT,
              due_date TEXT)''')
conn.commit()

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет {user.mention_html()}! Я - бот-напоминалка, я помогу тебе сэкономить много времени! Напиши /help тобы узнать список команд.",
        reply_markup=markup
    )


async def help(update, context):
    user = update.effective_user
    await update.message.reply_text(
        "/new_task - создать новую задачу;\n"
        "/show_tasks - показать список твоих активных задач;\n"
        "/delete_task - удалить одну из задач;\n"
        "/delete_all_tasks - удалить все задачи")


async def new_task(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"Напиши имя задачи:",
    )


async def show_tasks(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"",
    )


async def delete_task(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"",
    )


async def delete_all_tasks(update, context):
    user = update.effective_user
    await update.message.reply_text(
        rf"",
    )


def main():
    # Создаём объект Application.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("new_task", new_task))
    application.add_handler(CommandHandler("show_tasks", show_tasks))
    application.add_handler(CommandHandler("delete_task", delete_task))
    application.add_handler(CommandHandler("delete_all_tasks", delete_all_tasks))


    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
