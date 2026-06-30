import mysql.connector

def show_seats(cursor, show_id):
    """Displays the seat layout for a given showtime."""
    try:
        cursor.execute(
            "SELECT seat_row, seat_num, booked FROM Seats WHERE show_id=%s ORDER BY seat_row, seat_num", 
            (show_id,)
        )
        seats = cursor.fetchall()
        print("\n--- SCREEN ---")
        current_row = None
        for row, num, booked in seats:
            if row != current_row:
                if current_row is not None:
                    print() 
                print(row, end=": ")
                current_row = row
            symbol = "[X]" if booked else f"[{num}]"
            print(symbol, end=" ")
        print("\n\n(X = booked)\n")
    except mysql.connector.Error as err:
        print(f"\n❌ Error fetching seats: {err}")
