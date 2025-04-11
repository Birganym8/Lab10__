import psycopg2
import csv

# Подключение к базе данных
conn = psycopg2.connect(
    host="localhost",
    database="postgres",
    user="postgres",
    password="Aselek18"
)
cur = conn.cursor()


# Создание таблицы
def create_table():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100) NOT NULL,
            phone VARCHAR(20) NOT NULL
        )
    """)
    conn.commit()
    print("Таблица создана.")


# Вставка данных из CSV
def insert_from_csv(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # пропускаем заголовок
        for row in reader:
            if len(row) >= 2:
                cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (row[0], row[1]))
    conn.commit()
    print("Данные загружены из CSV.")


# Вставка вручную
def insert_from_input():
    name = input("Введите имя: ")
    phone = input("Введите телефон: ")
    cur.execute("INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)", (name, phone))
    conn.commit()
    print("Данные добавлены.")


# Обновление данных
def update_data():
    old_value = input("Введите имя или телефон, который хотите изменить: ")
    field = input("Что вы хотите обновить? (name/phone): ").strip().lower()
    new_value = input("Введите новое значение: ")

    if field == 'name':
        cur.execute("UPDATE phonebook SET first_name = %s WHERE first_name = %s OR phone = %s", (new_value, old_value, old_value))
    elif field == 'phone':
        cur.execute("UPDATE phonebook SET phone = %s WHERE first_name = %s OR phone = %s", (new_value, old_value, old_value))
    else:
        print("Неверный выбор поля.")
        return

    conn.commit()
    print("Данные обновлены.")


# Запросы с фильтрами
def search_data():
    print("Фильтрация данных:")
    search_type = input("Введите фильтр (all/name/phone): ").strip().lower()
    if search_type == 'all':
        cur.execute("SELECT * FROM phonebook")
    elif search_type == 'name':
        name = input("Введите имя для поиска: ")
        cur.execute("SELECT * FROM phonebook WHERE first_name ILIKE %s", (f"%{name}%",))
    elif search_type == 'phone':
        phone = input("Введите телефон для поиска: ")
        cur.execute("SELECT * FROM phonebook WHERE phone ILIKE %s", (f"%{phone}%",))
    else:
        print("Неверный фильтр.")
        return

    rows = cur.fetchall()
    for row in rows:
        print(row)
    if not rows:
        print("Ничего не найдено.")


# Удаление
def delete_data():
    choice = input("Удалить по (name/phone): ").strip().lower()
    value = input("Введите значение для удаления: ")
    if choice == 'name':
        cur.execute("DELETE FROM phonebook WHERE first_name = %s", (value,))
    elif choice == 'phone':
        cur.execute("DELETE FROM phonebook WHERE phone = %s", (value,))
    else:
        print("Неверный выбор.")
        return
    conn.commit()
    print("Данные удалены.")


# Главное меню
def main():
    create_table()

    while True:
        print("\n--- PhoneBook Меню ---")
        print("1. Загрузить данные из CSV")
        print("2. Добавить вручную")
        print("3. Обновить запись")
        print("4. Поиск")
        print("5. Удалить запись")
        print("6. Показать все")
        print("0. Выход")

        choice = input("Ваш выбор: ")
        if choice == '1':
            path = input("Введите путь к CSV-файлу: ")
            insert_from_csv(path)
        elif choice == '2':
            insert_from_input()
        elif choice == '3':
            update_data()
        elif choice == '4':
            search_data()
        elif choice == '5':
            delete_data()
        elif choice == '6':
            cur.execute("SELECT * FROM phonebook")
            for row in cur.fetchall():
                print(row)
        elif choice == '0':
            break
        else:
            print("Неверный ввод. Попробуйте снова.")

    cur.close()
    conn.close()
    print("Соединение закрыто.")


if __name__ == "__main__":
    main()
