#!env/bin/python
from dateutil.parser import parse
from flask import abort, Flask, jsonify, request

from scrape_voter_registration import get_registration

app = Flask(__name__)

DATE_FORMAT = '%m/%d/%Y'
DEFAULT_COUNTY = 'PHILADELPHIA'
ERROR_MESSAGE = {'error': 'Unknown error encountered attempting to get registration status.'}

DESCRIPTION = {
    'info': 'This endpoint passes along voter registration validation requests to ' +
            'https://www.pavoterservices.state.pa.us, then returns the info found as JSON. ' +
            'Returns empty object if unhandled error encountered. ' +
            'To use, POST JSON.',
    'exampleRequest': {
        'firstName':'firstname',
        'middleName': 'veryoptional',
        'lastName':'lastname',
        'dob': 'MM/DD/YYYY',
        'county':'Philadelphia'
    },
    'exampleGoodResponse': {
      'registration': {
        'county': 'PHILA', 
        'division': '00', 
        'dob': 'DD/MM/YYYY', 
        'name': 'FIRST MIDDLE LAST', 
        'party': 'PARTY', 
        'polling_place': {
          'accessibility': 'String describing handicap accessibility', 
          'address': {
            'city': 'PHILADELPHIA', 
            'state': 'PA', 
            'street': '111 SOME ST'
          }, 
          'name': 'POLLING LOCATION NAME'
        }, 
        'status': 'ACTIVE', 
        'ward': '00'
      }
    },
    'exampleResponseNotFound': {
        'registration': {
            'notFound': 'No Voter Registration information could be found for the data provided.'
        }
    },
    'exampleErrorResponse': {
        'registration': ERROR_MESSAGE
    }
}


@app.route('/pavoter', methods=['POST', 'GET'])
def get_voterinfo():
    if request.method == 'GET':
        return jsonify({'description': DESCRIPTION})
    required_fields = ['firstName', 'lastName', 'dob']
    if not request.json:
        abort(400)
    for fld in required_fields:
        if not fld in request.json:
            abort(400)

    try:
        county = request.json.get('county', DEFAULT_COUNTY)
        middle_name = request.json.get('middleName', None)
        if middle_name and len(middle_name.strip() < 1):
            middle_name = None
        first_name = request.json.get('firstName')
        last_name = request.json.get('lastName')
        dob = request.json.get('dob')
        try:
            # convert date to mm/dd/yyyy format
            dob_date = parse(dob)
            dob = dob_date.strftime(DATE_FORMAT)
        except:
            abort(400)

        response = get_registration(county, first_name, middle_name, last_name, dob)
    except:
        response = jsonify({'registration': ERROR_MESSAGE})

    if not response:
        response = jsonify({'registration': ERROR_MESSAGE})

    return jsonify({'registration': response})

@app.route('/')
def index():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(debug=True)
