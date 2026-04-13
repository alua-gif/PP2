import psycopg2
from config import load_config


def create_table():
    """Create the phonebook table if it doesn't exist."""
    command = """
    CREATE TABLE IF NOT EXISTS phonebook (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL,
        phone VARCHAR(20) NOT NULL
    );
    """

    conn = None
    try:
        config = load_config()
        conn = psycopg2.connect(**config)
        cur = conn.cursor()
        cur.execute(command)
        conn.commit()
        cur.close()
        print("Table 'phonebook' is ready.")
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def upsert_user():
    username = input("Enter username: ").strip()
    phone = input("Enter phone: ").strip()
    sql = "CALL upsert_u(%s, %s);"

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (username, phone))
            conn.commit()
            print(f"User '{username}' inserted/updated successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def insert_many_users():
    print("Enter list of usernames separated by space:")
    users = input().split()

    print("Enter list of phones separated by space:")
    phones = input().split()

    if len(users) != len(phones):
        print("Error: number of usernames and phones must match.")
        return

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            conn.notices.clear()
            with conn.cursor() as cur:
                cur.execute("CALL loophz(%s, %s);", (users, phones))
            conn.commit()

            if conn.notices:
                print("Incorrect data found:")
                for notice in conn.notices:
                    print(notice.strip())
            else:
                print("All users inserted successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def delete_contact():
    print("Delete by:")
    print("1. Username")
    print("2. Phone")
    choice = input("Choose: ").strip()

    if choice == "1":
        value = input("Enter username: ").strip()
    elif choice == "2":
        value = input("Enter phone: ").strip()
    else:
        print("Invalid choice.")
        return

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute("CALL del_user(%s);", (value,))
            conn.commit()
            print("Contact deleted successfully.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def search_records():
    pattern = input("Enter part of username or phone to search: ").strip()
    sql = "SELECT * FROM records(%s) ORDER BY out_id;"

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (pattern,))
                rows = cur.fetchall()

                if rows:
                    print("\nMatching contacts:")
                    for row in rows:
                        print(f"ID: {row[0]}, Username: {row[1]}, Phone: {row[2]}")
                else:
                    print("No matching contacts found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def paginated_data():
    try:
        lim = int(input("Enter LIMIT: ").strip())
        offs = int(input("Enter OFFSET: ").strip())
    except ValueError:
        print("Limit and offset must be integers.")
        return

    sql = "SELECT * FROM pagination(%s, %s) ORDER BY out_id;"

    config = load_config()
    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (lim, offs))
                rows = cur.fetchall()

                if rows:
                    print("\nPaginated contacts:")
                    for row in rows:
                        print(f"ID: {row[0]}, Username: {row[1]}, Phone: {row[2]}")
                else:
                    print("No data found.")
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)


def main():
    while True:
        print("\n--- PHONEBOOK MENU ---")
        print("1. Create table")
        print("2. Insert or update one user")
        print("3. Insert many users")
        print("4. Delete contact")
        print("5. Search matching records")
        print("6. Show paginated data")
        print("7. Exit")

        try:
            choice = int(input("Choose an option: ").strip())
        except ValueError:
            print("Please enter a number.")
            continue

        if choice == 1:
            create_table()
        elif choice == 2:
            upsert_user()
        elif choice == 3:
            insert_many_users()
        elif choice == 4:
            delete_contact()
        elif choice == 5:
            search_records()
        elif choice == 6:
            paginated_data()
        elif choice == 7:
            print("Bye.")
            break
        else:
            print("Invalid option. Try again.")


if __name__ == "__main__":
    main()
    