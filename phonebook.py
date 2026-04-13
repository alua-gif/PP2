import csv
from connect import connect
def create_table():
    conn = connect()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS phonebook (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            phone VARCHAR(20)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("Table created")

def insert_console():
    name = input("Name: ")
    phone = input("Phone: ")

    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)",
        (name, phone)
    )

    conn.commit()
    cur.close()
    conn.close()
    print("Inserted")


def insert_csv(filename):
    conn = connect()
    cur = conn.cursor()

    with open(filename, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader, None)

        for row in reader:
            if len(row) >= 2:
                cur.execute(
                    "INSERT INTO phonebook (first_name, phone) VALUES (%s, %s)",
                    (row[0], row[1])
                )

    conn.commit()
    cur.close()
    conn.close()
    print("CSV inserted")


def update_name(old, new):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE phonebook SET first_name=%s WHERE first_name=%s",
        (new, old)
    )

    conn.commit()

    if cur.rowcount == 0:
        print("No such contact")
    else:
        print("Name updated")

    cur.close()
    conn.close()


def update_phone(name, new_phone):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "UPDATE phonebook SET phone=%s WHERE first_name=%s",
        (new_phone, name)
    )

    conn.commit()

    if cur.rowcount == 0:
        print("No such contact")
    else:
        print("Phone updated")

    cur.close()
    conn.close()


def show_all():
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook")
    rows = cur.fetchall()

    for row in rows:
        print(row)

    cur.close()
    conn.close()


def find_by_name(name):
    conn = connect()
    cur = conn.cursor()

    cur.execute("SELECT * FROM phonebook WHERE first_name=%s", (name,))
    rows = cur.fetchall()
    print(rows)

    cur.close()
    conn.close()


def find_by_prefix(prefix):
    conn = connect()
    cur = conn.cursor()

    cur.execute(
        "SELECT * FROM phonebook WHERE phone LIKE %s",
        (prefix + "%",)
    )

    rows = cur.fetchall()
    print(rows)

    cur.close()
    conn.close()


def delete_by_name(name):
    conn = connect()
    cur = conn.cursor()

    cur.execute("DELETE FROM phonebook WHERE first_name=%s", (name,))
    conn.commit()

    if cur.rowcount == 0:
        print("No such contact")
    else:
        print("Deleted by name")

    cur.close()
    conn.close()


def delete_by_phone(phone):
    conn = connect()
    cur = conn.cursor()
    cur.execute("DELETE FROM phonebook WHERE phone=%s", (phone,))
    conn.commit()

    if cur.rowcount == 0:
        print("No such contact")
    else:
        print("Deleted by phone")

    cur.close()
    conn.close()


def menu():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create table")
        print("2. Insert from console")
        print("3. Insert from CSV")
        print("4. Update name")
        print("5. Update phone")
        print("6. Show all")
        print("7. Find by name")
        print("8. Find by phone prefix")
        print("9. Delete by name")
        print("10. Delete by phone")
        print("0. Exit")

        choice = input("Choose: ")

        if choice == "1":
            create_table()
        elif choice == "2":
            insert_console()
        elif choice == "3":
            filename = input("CSV filename: ")
            insert_csv(filename)
        elif choice == "4":
            old = input("Old name: ")
            new = input("New name: ")
            update_name(old, new)
        elif choice == "5":
            name = input("Name: ")
            new_phone = input("New phone: ")
            update_phone(name, new_phone)
        elif choice == "6":
            show_all()
        elif choice == "7":
            name = input("Name: ")
            find_by_name(name)
        elif choice == "8":
            prefix = input("Prefix: ")
            find_by_prefix(prefix)
        elif choice == "9":
            name = input("Name: ")
            delete_by_name(name)
        elif choice == "10":
            phone = input("Phone: ")
            delete_by_phone(phone)
        elif choice == "0":
            print("Bye")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    menu()