from flask import Flask, render_template, request, redirect, url_for, flash 

app = Flask(__name__, static_folder='static')
app.secret_key = "supersecretkey"

bookings = [
    {"id": 1, "departure": "Toronto to Calgary", "date": "Tuesday, October 8th, 2024", "time": "08:00 - 12:24", "airline": "WestJet"},
    {"id": 2, "departure": "Calgary to Toronto", "date": "Friday, October 18th, 2024", "time": "1:49 - 6:32", "airline": "Air Canada"}
]

@app.route('/')
def cancelBooking ():
    return render_template('cancelBooking.html', bookings=bookings)

@app.route('/cancel/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    global bookings
    booking_to_cancel = next((b for b in bookings if b['id'] == booking_id), None)

    if booking_to_cancel:
        bookings.remove(booking_to_cancel)
        flash(f"Your booking from {booking_to_cancel['departure']} on {booking_to_cancel['date']} has been canceled successfully.")
        
    else:
        flash('Booking not found.')

    return redirect(url_for('cancelBooking'))  

if __name__ == '__main__':
    app.run(debug=True)