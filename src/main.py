import mysql.connector
from datetime import datetime, timedelta, date, time
from booking import show_seats

def _generate_seats_for_show(cursor, show_id, movie_id):
    try:
        seat_rows = ['A', 'B', 'C', 'D', 'E']
        seat_nums_per_row = 6
        for row in seat_rows:
            for num in range(1, seat_nums_per_row + 1):
                cursor.execute(
                    "INSERT INTO Seats(show_id, seat_row, seat_num, booked, movie_id) VALUES(%s, %s, %s, %s, %s)",
                    (show_id, row, num, 0, movie_id)
                )
    except mysql.connector.Error as err:
        print(f"❌ Error generating seats: {err}")
        raise 

def add_movie(con, cursor):
    try:
        name = input("Enter movie name: ")
        genre = input("Enter genre: ")
        category = input("Enter category (Cool 2D / Premium 2D / IMAX): ")
        price = int(input("Enter ticket price: "))
        
        cursor.execute(
            "INSERT INTO Movies(name, genre, category, price) VALUES(%s, %s, %s, %s)",
            (name, genre, category, price)
        )
        movie_id = cursor.lastrowid

        cursor.execute("SELECT MAX(screen_number) FROM Showtimes")
        max_screen = cursor.fetchone()[0]
        screen_number = (max_screen or 0) + 1
        print(f"\nAssigning movie to Screen {screen_number} for default showtimes...")

        today = date.today()
        default_showtimes = [time(10, 0), time(14, 0), time(18, 0)]
        for i in range(7):
            show_date = today + timedelta(days=i)
            for t in default_showtimes:
                cursor.execute(
                    "INSERT INTO Showtimes(movie_id, screen_number, show_date, show_time) VALUES(%s, %s, %s, %s)",
                    (movie_id, screen_number, show_date, t)
                )
                show_id = cursor.lastrowid
                _generate_seats_for_show(cursor, show_id, movie_id)
        con.commit() 
        print(f"\n✅ Movie '{name}' and default showtimes added successfully!")
    except ValueError:
        print("\n❌ Invalid input. Price must be a number.")
        con.rollback()
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")
        con.rollback()

def show_movies(cursor):
    try:
        cursor.execute("SELECT movie_id, name, genre, category, price FROM Movies")
        movies = cursor.fetchall()
        if not movies:
            print("\n❌ No movies available.")
            return
        print("\n------------ Available Movies ------------")
        print("ID | Name | Genre | Category | Price")
        for movie_id, name, genre, category, price in movies:
            print(f"🎬 {movie_id} | {name} | {genre} | {category} | Rs.{price}")
        print("----------------------------------------")
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")

def edit_showtimes(con, cursor):
    show_movies(cursor)
    try:
        movie_id = int(input("Enter movie ID to edit showtimes: "))
        print("1. Add showtime")
        print("2. Delete showtime")
        choice = input("Enter choice: ")
        if choice == "1":
            date_input = input("Enter show date (YYYY-MM-DD): ")
            time_input = input("Enter show time (HH:MM): ")
            show_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            show_time = datetime.strptime(time_input, "%H:%M").time()
            
            cursor.execute("SELECT MAX(screen_number) FROM Showtimes")
            max_screen = cursor.fetchone()[0]
            screen_number = (max_screen or 0) + 1
            cursor.execute(
                "INSERT INTO Showtimes(movie_id, screen_number, show_date, show_time) VALUES(%s,%s,%s,%s)",
                (movie_id, screen_number, show_date, show_time)
            )
            show_id = cursor.lastrowid
            _generate_seats_for_show(cursor, show_id, movie_id)
            con.commit()
            print("✅ Showtime added successfully.")
        elif choice == "2":
            date_input = input("Enter show date (YYYY-MM-DD): ")
            time_input = input("Enter show time (HH:MM): ")
            show_date = datetime.strptime(date_input, "%Y-%m-%d").date()
            show_time = datetime.strptime(time_input, "%H:%M").time()
            cursor.execute(
                "SELECT show_id FROM Showtimes WHERE movie_id=%s AND show_date=%s AND show_time=%s",
                (movie_id, show_date, show_time)
            )
            show = cursor.fetchone()
            if show:
                show_id = show[0]
                cursor.execute("DELETE FROM Seats WHERE show_id=%s", (show_id,))
                cursor.execute("DELETE FROM Showtimes WHERE show_id=%s", (show_id,))
                con.commit()
                print("✅ Showtime deleted.")
            else:
                print("❌ No such showtime found.")
    except (ValueError, IndexError):
        print("\n❌ Invalid input. Please check formats.")
        con.rollback()
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")
        con.rollback()

def delete_movie(con, cursor):
    show_movies(cursor)
    try:
        movie_id = int(input("Enter movie ID to delete: "))
        cursor.execute("DELETE FROM Bill WHERE movie_name=(SELECT name FROM Movies WHERE movie_id=%s)", (movie_id,))
        cursor.execute("DELETE FROM Seats WHERE movie_id=%s", (movie_id,))
        cursor.execute("DELETE FROM Showtimes WHERE movie_id=%s", (movie_id,))
        cursor.execute("DELETE FROM Movies WHERE movie_id=%s", (movie_id,))
        if cursor.rowcount > 0:
            con.commit()
            print("❌ Movie and all related data deleted successfully!")
        else:
            print("❌ Movie ID not found.")
    except ValueError:
        print("\n❌ Invalid input. Movie ID must be a number.")
        con.rollback()
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")
        con.rollback()

def book_ticket(con, cursor):
    show_movies(cursor)
    try:
        movie_id = int(input("Enter Movie ID: "))
        date_input = input("Enter Date (YYYY-MM-DD): ")
        time_input = input("Enter Time (HH:MM): ")
        show_date = datetime.strptime(date_input, "%Y-%m-%d").date()
        show_time = datetime.strptime(time_input, "%H:%M").time()
        
        cursor.execute(
            "SELECT show_id, screen_number FROM Showtimes WHERE movie_id=%s AND show_date=%s AND show_time=%s",
            (movie_id, show_date, show_time)
        )
        show = cursor.fetchone()
        if not show:
            print("❌ No such showtime found.")
            return
        show_id, screen_number = show
        show_seats(cursor, show_id)
        
        name = input("Enter your name: ")
        seat_choice = input("Enter seat (e.g., A3): ").upper()
        row = seat_choice[0]
        num = int(seat_choice[1:])

        # --- CONCURRENCY PROTECTION RACE-CONDITION LOCK ---
        cursor.execute(
            "UPDATE Seats SET booked=1 WHERE show_id=%s AND seat_row=%s AND seat_num=%s AND booked=0",
            (show_id, row, num)
        )
        if cursor.rowcount > 0: 
            cursor.execute("SELECT name, category, price FROM Movies WHERE movie_id=%s", (movie_id,))
            movie_name, category, price = cursor.fetchone()
            discount = 50 if num in (1, 6) else 0
            total_price = price - discount
            
            cursor.execute(
                "INSERT INTO Bill(customer_name, movie_name, seat, category, total_price, show_date, show_time, screen_number) VALUES(%s, %s, %s, %s, %s, %s, %s, %s)",
                (name, movie_name, seat_choice, category, total_price, date_input, time_input, screen_number)
            )
            con.commit()
            print("\n🎟 Ticket Booked Successfully!")
        else:
            print("❌ Seat not available or already booked! Please try another seat.")
            con.rollback()
    except (ValueError, IndexError):
        print("\n❌ Invalid input configuration.")
        con.rollback()
    except mysql.connector.Error as err:
        print(f"\n❌ Database error during booking: {err}")
        con.rollback()

def show_bills(cursor):
    try:
        cursor.execute("SELECT bill_id, customer_name, movie_name, seat, total_price, show_date, show_time, screen_number FROM Bill")
        bills = cursor.fetchall()
        if not bills:
            print("\n--- No bills found. ---")
            return
        print("\n--- All Bills ---")
        for b_id, c_name, m_name, seat, price, s_date, s_time, s_num in bills:
            print(f"{b_id} | {c_name} | {m_name} | {seat} | Rs.{price} | {s_date} | {s_time} | {s_num}")
    except mysql.connector.Error as err:
        print(f"\n❌ Database error: {err}")

def main():
    try:
        con = mysql.connector.connect(
            host="localhost",
            user="root",
            password="password", 
            database="cts"
        )
        cursor = con.cursor()
        while True:
            print("\n========= Movie Ticketing System =========")
            print("1. Add Movie")
            print("2. Show Movies")
            print("3. Book Ticket")
            print("4. Edit Showtimes")
            print("5. Delete Movie")
            print("6. Show All Bills")
            print("7. Exit")
            ch = input("\nEnter choice: ")
            if ch == "1": add_movie(con, cursor)
            elif ch == "2": show_movies(cursor)
            elif ch == "3": book_ticket(con, cursor)
            elif ch == "4": edit_showtimes(con, cursor)
            elif ch == "5": delete_movie(con, cursor)
            elif ch == "6": show_bills(cursor)
            elif ch == "7": break
    except mysql.connector.Error as err:
        print(f"\n❌ CRITICAL: Could not connect to MySQL Server: {err}")
    finally:
        if 'con' in locals() and con.is_connected():
            cursor.close()
            con.close()

if __name__ == "__main__":
    main()
