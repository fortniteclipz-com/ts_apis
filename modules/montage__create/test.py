import run
import json

bodies = [{
    'stream_user': 'test_stream_user',
    'stream_id': 311038404,
    'clips': [{
        'time_in': 1593.699742,
        'time_out': 1598.455016,
    } , {
        'time_in': 1593.699742,
        'time_out': 1598.455016,
    }],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

