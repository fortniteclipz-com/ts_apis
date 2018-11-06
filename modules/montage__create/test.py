import run
import json

bodies = [{
    'stream_id': "308990189",
    'clips': [{
        'time_in': 1941,
        'time_out': 1947,
    }, {
        'time_in': 1966,
        'time_out': 1971,
    }, {
        'time_in': 2304,
        'time_out': 2310,
    }, {
        'time_in': 4497,
        'time_out': 4504,
    }, {
        'time_in': 4553,
        'time_out': 4559,
    }]
}]

for body in bodies:
    event = {
        'body': json.dumps(body),
        'requestContext': {'authorizer': {'claims': {'cognito:username': 'development_test_username'}}}}
    run.run(event, {})

