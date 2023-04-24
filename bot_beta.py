import datetime
import logging
import sqlite3
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import CommandHandler, ConversationHandler
from telegram import ReplyKeyboardMarkup

TOKEN = '6034472814:AAGQMRiI97yXXlIlok6yC0K08eCZTSILFf0'

#
reply_keyboard = [['/new', '/show_all'],
                  ['/delete', '/delete_all']]
markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)

# создаем дб где будем хранить список задач
conn = sqlite3.connect('tasks.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER,
              task STRING,
              date STRING)''')
conn.commit()

# Запускаем логгирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)


#
async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я - твой тайм-менеджер, я помогу тебе сэкономить много драгоценного времени!\n"
        "Чтобы узнать список команд, напиши /help.",
        reply_markup=markup
    )


#
async def help(update, context):
    user = update.effective_user
    await update.message.reply_text(
        "/new <name> <time> - создать новую задачу;\n"
        "/show_all - показать список твоих активных задач;\n"
        "/delete <task_id> - удалить одну из задач по номеру;\n"
        "/delete_all - удалить все задачи")


#
async def new_task(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    msg = update.message.text.split()[1:]
    if len(msg) < 2:
        await update.message.reply_text(
            "Неправильный формат ввода",
        )
        return 0
    task = msg[0:-1]
    date = msg[-1]
    c.execute("INSERT INTO tasks (user_id, task, date) VALUES (?, ?, ?)", (user_id, ' '.join(task), date))
    conn.commit()
    await update.message.reply_text(
        'Задача добавлена, это успех!',
    )
    # print(f'Added new task: {user_id}, {" ".join(task)}, {date}')


#
def print_rows_by_id(id):
    # формируем запрос на выборку строк с заданным id
    query = f"SELECT * FROM tasks WHERE user_id = {id}"

    c.execute(query) # выполняем запрос
    rows = c.fetchall() # получаем все найденные строки результата

    if rows:
        return rows
    else:
        return 'Похоже, ты ничего не запланировал!'


#
async def show_tasks(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    await update.message.reply_text(
        print_rows_by_id(user_id),
    )


#
async def delete_task(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    msg = update.message.text.split()[1:]
    if len(msg) != 1:
        await update.message.reply_text(
            "Неправильный формат ввода",
        )
        return 0
    task_id = msg[0]
    # print(task_id, user_id)
    #
    c.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
    row = c.fetchone()

    if row is not None:
        # Если строка найдена, удаляем ее
        c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        conn.commit()
        await update.message.reply_text(
            f'Хорошо, задача под номером {task_id} удаленa',
        )
    else:
        await update.message.reply_text(
            f'Задача с номером {task_id} не найдена!',
        )


#
async def delete_all(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    c.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))
    await update.message.reply_text(
        "Успех! Удалено всё то, что может быть удалено",
    )


# функция которая будет отправлять напоминания в нужное время
async def remind():
    pass


def main():
    # Создаём объект Application.
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("new", new_task))
    application.add_handler(CommandHandler("show_all", show_tasks))
    application.add_handler(CommandHandler("delete", delete_task))
    application.add_handler(CommandHandler("delete_all", delete_all))


    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main()
if __name__ == '__main__':
    main()
