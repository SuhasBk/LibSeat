#!/usr/local/bin/python3
import os, sys
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from flask_cors import CORS
from libseat import get_next_delta, search, add, bulk_book, room_mappings
from calendar_service import send_email_with_invite
from datetime import datetime
import pytz

app = Flask(__name__)
api = Api(app)
CORS(app)

libData = {
    'lid': 10450,
    'zone': 5909,
    'gid': 29456,
}

@app.route("/")
def home():
    return render_template('index.html')

class Search(Resource):
    def post(self):
        data = request.get_json()
        metaData = libData.copy()
        metaData['itemId'] = int(data['itemId'])
        metaData['fname'] = data['fname']
        metaData['lname'] = data['lname']
        metaData['email'] = data['email']
        metaData['startDate'] = data['startDate']
        metaData['endDate'] = get_next_delta(metaData['startDate'], 'days', 1)

        available_seats = search(metaData)
        return {'slots': available_seats}

class ReserveSlots(Resource):
    def post(self):
        res = 'Something went wrong! Try again later'
        data = request.get_json()
        metaData = libData.copy()
        metaData['itemId'] = int(data['itemId'])
        metaData['fname'] = data['fname']
        metaData['lname'] = data['lname']
        metaData['email'] = data['email']
        metaData['startDate'] = data['startDate']
        metaData['endDate'] = get_next_delta(metaData['startDate'], 'days', 1)

        try:
            bookings = []

            for i, slot in enumerate(data['bookings'], 1):
                times = slot['time'].split(' to ')
                metaData['time'] = times[0]

                slot['checksum'] = add(metaData, slot['checksum'])
                if not slot['checksum']:
                    raise InterruptedError(res)
                
                bookings.append({
                    'id': i,
                    'eid': metaData['itemId'],
                    'seat_id': 0,
                    'gid': metaData['gid'],
                    'lid': metaData['lid'],
                    'start': metaData['startDate'] + ' ' + times[0],
                    'end': metaData['startDate'] + ' ' + times[1],
                    'checksum': slot['checksum']
                })
            
            metaData['bookings'] = bookings
            res = bulk_book(metaData)

            startTime = datetime.strptime(data['startDate'] + 'T' + data['bookings'][0]['time'].split(' to ')[0], '%Y-%m-%dT%H:%M').replace(tzinfo=pytz.timezone('America/Chicago'))
            endTime = datetime.strptime(data['startDate'] + 'T' + data['bookings'][len(bookings) - 1]['time'].split(' to ')[1], '%Y-%m-%dT%H:%M').replace(tzinfo=pytz.timezone('America/Chicago'))

            # Event details
            event_details = {
                'summary': 'Library Room Scheduled',
                'start': startTime,
                'end': endTime,
                'location': f'UTA Central Library - {room_mappings[metaData["itemId"]]}',
                'description': 'Study/Work/Entertainment Time'
            }

            # Send the email
            send_email_with_invite(
                sender_email=os.environ['EMAIL_ID'],
                sender_password=os.environ['EMAIL_PASSWORD'],
                recipient_email='sxk7070@mavs.uta.edu',
                subject=f'Room (possibly, intermittently) Scheduled from {startTime} to {endTime} on {metaData["startDate"]}',
                body='Please find the meeting invite attached.',
                event_details=event_details
            )
        except InterruptedError:
            return {'err': res}
        
        return {
            'msg': res
        }

api.add_resource(Search, '/api/v1/search')
api.add_resource(ReserveSlots, '/api/v1/reserve')

if __name__=='__main__':
    try:
        ip = sys.argv[1]
        port = sys.argv[2]
    except IndexError:
        ip = "0.0.0.0"
        port = 8000
    
    debug = True if os.environ.get("HIDDEN_ID") == 'BATMAN' else False

    app.run(host=ip,debug=debug,port=port)
