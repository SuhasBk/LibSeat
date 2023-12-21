#!/usr/local/bin/python3
from flask import Flask, render_template, request
from libseat import room_mappings, headers, metaData, get_next_delta, search, add, book

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/reserve", methods=['GET', 'POST'])
def reserve():
    if request.method == 'POST':
        data = request.form
        metaData['itemId'] = int(data['itemId'])
        metaData['fname'] = data['fname']
        metaData['lname'] = data['lname']
        metaData['email'] = data['email']
        metaData['startDate'] = data['dateTime'].split('T')[0]
        metaData['time'] = data['dateTime'].split('T')[1]
        metaData['endDate'] = get_next_delta(metaData['startDate'], 'days', 1)

        available_seats, seat_checksum = search()
        if not seat_checksum:
            return render_template('available.html', available_seats=available_seats, msg='Seat not available at that slot! Pick one from available ones below:')

        # reserve and book it!
        new_checksum = add(seat_checksum)
        book(new_checksum)
    elif request.method == 'GET':
        return 'violation! you are in the wrong place at the wrong time!'
    
    return '<h1>Your reservation was successful! 🤙</h1>'

app.run(port=8000, debug=True)