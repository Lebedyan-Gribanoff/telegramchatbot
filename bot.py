# импортируем библиотеки
import datetime  # чтобы определять текущее время
import logging
import sqlite3
import asyncio
from telegram.ext import Application
from telegram.ext import CommandHandler
from telegram import ReplyKeyboardMarkup

# токен бота
TOKEN = '6034472814:AAGQMRiI97yXXlIlok6yC0K08eCZTSILFf0'

# добавляем кавиатуру
reply_keyboard = [['/new', '/show_all'],
                  ['/delete', '/delete_all'],
                  ['/remind']]
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


# начальная команда
async def start(update, context):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет {user.mention_html()}! Я твой тайм-менеджер, я помогу тебе сэкономить много драгоценного времени!\n"
        "Чтобы узнать список команд, напиши /help.",
        reply_markup=markup
    )


# команда помощи
async def help(update, context):
    user = update.effective_user
    await update.message.reply_text(
        "/new <name> <time> - создать новую задачу, ремя в формате 2023-04-25 12:00;\n"
        "/show_all - показать список твоих активных задач;\n"
        "/delete <task_id> - удалить одну из ваших задач по номеру;\n"
        "/delete_all - удалить все задачи;\n"
        "/remind - бот начнет отправлять напоминания по времени.")


# функция добавления новой задачи
async def new_task(update, context):
    user = update.effective_user
    user_id = update.message.chat_id  # получаем айди пользователя для бд
    msg = update.message.text.split()[1:]  # получаем всё сообщение пользователя
    if len(msg) < 2:
        await update.message.reply_text(
            # если нет даты или текста задания выводим ошибку
            "Неправильный формат ввода",
        )
        return 0
    task = msg[0:-2]  # получаем текст задачи
    date = msg[-2] + ' ' + msg[-1]  # получаем дату задачи
    c.execute("INSERT INTO tasks (user_id, task, date) VALUES (?, ?, ?)", (user_id, ' '.join(task), date))
    # добавляем в базу данных
    conn.commit()
    await update.message.reply_text(
        'Задача добавлена, это успех!',
    )
    # print(f'Added new task: {user_id}, {" ".join(task)}, {date}')


# функция вывода всех задач одного пользователя
def print_rows_by_id(id):
    # формируем запрос на поиск строк пользователя
    query = f"SELECT * FROM tasks WHERE user_id = {id}"

    c.execute(query)  # выполняем запрос
    rows = c.fetchall()  # получаем все найденные строки
    conn.commit()

    if rows:
        return rows
    else:
        return 'Похоже, ты ничего не запланировал!'


async def show_tasks(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    await update.message.reply_text(
        print_rows_by_id(user_id),  # вызываем функцию вывода задач пользователя
    )


# функция удаления определенной задачи
async def delete_task(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    msg = update.message.text.split()[1:]  # получаем текст сообщения пользователя
    if len(msg) != 1:
        # если пользователь не ввел айди задачи
        await update.message.reply_text(
            "Неправильный формат ввода",
        )
        return 0
    task_id = msg[0]  # получаем айди задачи
    # print(task_id, user_id)
    # ищем строку
    c.execute("SELECT * FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))  #
    row = c.fetchone()
    conn.commit()

    if row is not None:
        # если эта задача принадлежит нашему пользователю, удаляем
        c.execute("DELETE FROM tasks WHERE id=? AND user_id=?", (task_id, user_id))
        conn.commit()
        await update.message.reply_text(
            f'Хорошо, задача под номером {task_id} удаленa',
        )
    else:
        # если задачи нет
        await update.message.reply_text(
            f'Задача с номером {task_id} не найдена или пренадлежит другому пользователю!',
        )


# функция удаления всех задач
async def delete_all(update, context):
    user = update.effective_user
    user_id = update.message.chat_id
    c.execute("DELETE FROM tasks WHERE user_id=?", (user_id,))  # удаляем все задачи по айди пользователя
    conn.commit()
    await update.message.reply_text(
        "Успех! Удалено всё то, что может быть удалено",
    )


# функция, которая будет отправлять напоминания в нужное время
async def remind(update, cotext):
    user = update.effective_user
    user_id = update.message.chat_id

    query = f"SELECT * FROM tasks WHERE user_id = ?"  # делаем запрос на задачи
    c.execute(query, (user_id,))  # выполняем запрос
    rows = c.fetchall()  # получаем все найденные строки
    conn.commit()

    # если не нашлось задач пользователя
    if rows is None:
        await update.message.reply_text(
            'Похоже, ты ничего не запланировал!',
        )
        return 0

    else:
        await update.message.reply_text(
            "Хорошо, теперь я буду отправлять напоминания",
        )

        # главный цикл
        while True:
            now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')  # получаем текущее время
            print(now)

            c.execute("SELECT * FROM tasks WHERE date=? AND user_id=?", (now, user_id))  # ищем задачи пользователя
            # проверяем на актуальность даты
            rows = c.fetchall()
            conn.commit()

            if rows is not None:
                for row in rows:
                    task = row[2]
                    await update.message.reply_text(f"Напоминаю: {task}, время:{now}")
                    c.execute("DELETE FROM tasks WHERE task=? AND user_id=?", (task, user_id))
                    # выводим и удаляем актуальные задачи
                    conn.commit()

            c.execute(query, (user_id,))
            rows = c.fetchall()
            conn.commit()

            if rows is None:
                # если больше задач нет, прекращаем цикл
                await update.message.reply_text(
                    'Это была последняя задача',
                )
                return 0
            conn.commit()
            # ждем минуту перед следующей итерацией цикла
            await asyncio.sleep(60)


# главная функция
def main():
    # Создаём объект Application.
    application = Application.builder().token(TOKEN).build()

    # добавляяем команды в бота
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("new", new_task))
    application.add_handler(CommandHandler("show_all", show_tasks))
    application.add_handler(CommandHandler("delete", delete_task))
    application.add_handler(CommandHandler("delete_all", delete_all))
    application.add_handler(CommandHandler("remind", remind))

    # Запускаем приложение.
    application.run_polling()


# Запускаем функцию main()
if __name__ == '__main__':
    main()
