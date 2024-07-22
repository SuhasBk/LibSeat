#!/usr/local/bin/python3
import requests, json
from datetime import datetime, timedelta

# common header for all requests
headers = {
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
    111713: '519 (Capacity 5)',
    111714: '520A (Capacity 6)',
    111716: '520B (Capacity 3)',
    130324: '520C (Capacity 2)'
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

def search(metaData):
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
    print(data)
    if response.ok:
        seats = list(filter(lambda seat: 'className' not in seat and seat['itemId'] == metaData['itemId'], response.json()['slots']))
        return seats
    return []


def add(metaData, seat_checksum):
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

def bulk_book(metaData):
    bookings = json.dumps(metaData['bookings'])

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

''' + bookings + '''
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="returnUrl"

/space/111716
------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="pickupHolds"


------WebKitFormBoundaryhdaUJdAeBSWES7e8
Content-Disposition: form-data; name="method"

12
------WebKitFormBoundaryhdaUJdAeBSWES7e8--'''

    url = 'https://uta.libcal.com/ajax/space/book'
    custom_headers = headers.copy()
    custom_headers['content-type'] = 'multipart/form-data; boundary=----WebKitFormBoundaryhdaUJdAeBSWES7e8'
    
    response = requests.post(url, headers=custom_headers, data=data)
    response.ok and print('Seat booked successfully!')
    not response.ok and print('Failed to book your seat! Check payload.', response.text)

    if not response.ok:
        raise InterruptedError('Failed to book your seat! Please try again later.')
    
    return 'Seat booked successfully! Check your email for more details.'