#!/usr/local/bin/python3
from flask import Flask, render_template, request
from flask_restful import Api, Resource
from flask_cors import CORS
from libseat import get_next_delta, search, add, bulk_book

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
        except InterruptedError:
            return {'err': res}
        
        return {
            'msg': res
        }

api.add_resource(Search, '/api/v1/search')
api.add_resource(ReserveSlots, '/api/v1/reserve')

app.run(port=8000, debug=True)
