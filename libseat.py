#!/usr/local/bin/python3
import requests, os
from pyfiglet import figlet_format
from datetime import datetime, timedelta

metaData = {
    'lid': 10450,
    'zone': 5909,
    'gid': 29456,
}

# common header for all requests
headers = {
    'authority': 'uta.libcal.com',
    'accept': 'application/json, text/javascript, */*; q=0.01',
    'accept-language': 'en-US,en;q=0.9',
    'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'dnt': '1',
    'origin': 'https://uta.libcal.com',
    'referer': 'https://uta.libcal.com/space/111716',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'x-requested-with': 'XMLHttpRequest',
}

# hard-coded 5th floor room mappings
room_mappings = {
    '519 (Capacity 5)': 111713,
    '520A (Capacity 6)': 111714,
    '520B (Capacity 3)': 111716,
    '520C (Capacity 2)': 130324
}

def get_next_delta(dt, delta_type, delta_value):
    if delta_type == 'days':
        date = datetime.strptime(dt, "%Y-%m-%d")
        next_day = date + timedelta(days=delta_value)
        next_day_string = next_day.strftime("%Y-%m-%d")
        return next_day_string
    elif delta_type == 'minutes':
        time_obj = datetime.strptime(dt, "%H:%M")
        new_time = time_obj + timedelta(minutes=delta_value)
        end_time_string = new_time.strftime("%H:%M")
        return end_time_string

def choose_a_room():
    print('Enter the room you want in 5th floor:')
    for index, room in enumerate(room_mappings.keys()):
        print(index + 1, '--->', room)
    ch = int(input("\nEnter your choice:\n> ")) - 1
    return room_mappings[list(room_mappings.keys())[ch]]

def search():
    data = {
        'lid': metaData['lid'],
        'gid': metaData['gid'],
        'eid': metaData['itemId'],
        'seat': '0',
        'seatId': '0',
        'zone': metaData['zone'],
        'start': metaData['startDate'],
        'end': metaData['endDate'],
        'pageIndex': '0',
        'pageSize': '18'
    }

    url = 'https://uta.libcal.com/spaces/availability/grid'

    response = requests.post(url, headers=headers, data=data)
    if response.ok:
        seats = list(filter(lambda seat: 'className' not in seat and seat['itemId'] == metaData['itemId'], response.json()['slots']))
        
        for seat in seats:
            seat_time = seat['start'].split(' ')[1][:-3]
            if seat['itemId'] == metaData['itemId'] and seat_time == metaData['time']:
                return seats, seat['checksum']
    
        return seats, ''
        
    return [], ''


def add(seat_checksum):
    data = {
        'add[eid]': metaData['itemId'],
        'add[gid]': metaData['gid'],
        'add[lid]': metaData['lid'],
        'add[start]': metaData['startDate'] + ' ' + metaData['time'],
        'add[checksum]': seat_checksum,
        'lid': metaData['lid'],
        'gid': metaData['gid'],
        'start': metaData['startDate'],
        'end': metaData['endDate']
    }

    url = 'https://uta.libcal.com/spaces/availability/booking/add'

    response = requests.post(url, headers=headers, data=data)
    return response.json()['bookings'][0]['checksum'] if response.ok else ''


def book(checksum):
    end_time_string = get_next_delta(metaData['time'], 'minutes', 30)
    url = 'https://uta.libcal.com/ajax/space/book'
    headers['content-type'] = 'multipart/form-data; boundary=----WebKitFormBoundaryhdaUJdAeBSWES7e8'

    # <DO NOT TOUCH THIS FORMATTING OR INDENTATION
    data = f'''------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="session"

42106807
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="fname"

{metaData['fname']}
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="lname"

{metaData['lname']}
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="email"

{metaData['email']}
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="bookings"

[{{"id":1,"eid":{metaData['itemId']},"seat_id":0,"gid":{metaData['gid']},"lid":{metaData['lid']},"start":"{metaData['startDate']} {metaData['time']}","end":"{metaData['startDate']} {end_time_string}","checksum":"{checksum}"}}]
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="returnUrl"

/space/111716
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="pickupHolds"


------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="method"

12
------WebKitFormBoundaryhdaUJdAeBSWES7e8--'''
    # DO NOT TOUCH THIS FORMATTING OR INDENTATION>

    response = requests.post(url, headers=headers, data=data)
    response.ok and print('Seat booked successfully!')
    not response.ok and print('Failed to book your seat! Check payload.')