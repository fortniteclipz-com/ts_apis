import run
import json

bodies = [{
    'stream_id': "335886831",
    'clips': [{
        'time_in': 473,
        'time_out': 479,
    }, {
        'time_in': 606,
        'time_out': 612,
    }]
}]

for b in bodies:
    event = {
        'body': json.dumps(b),
        'requestContext': {'authorizer': {'claims': {'cognito:username': 'development-test-username'}}}
    }
    run.run(event, {})

