import datetime
import logging
import sqlite3
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler

TOKEN = '6034472814:AAGQMRiI97yXXlIlok6yC0K08eCZTSILFf0'

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
    )


async def help_command(update, context):
    user = update.effective_user
    await update.message.reply_html(
        rf"/create_task - создать новую задачу, /show_tasks - показать список твоих активных задач, /remove_task - удалить одну из задач",
    )


def main():
    # Создаём объект Application.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main() в случае запуска скрипта.
if __name__ == '__main__':
    main()
