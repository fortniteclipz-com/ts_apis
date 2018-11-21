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
    # }, {
    #     'time_in': 2304,
    #     'time_out': 2310,
    # }, {
    #     'time_in': 4497,
    #     'time_out': 4504,
    # }, {
    #     'time_in': 4553,
    #     'time_out': 4559,
    }]
}]

for body in bodies:
    event = {
        'body': json.dumps(body),
        'requestContext': {'authorizer': {'claims': {'cognito:username': 'development-test-username'}}}
    }
    run.run(event, {})

