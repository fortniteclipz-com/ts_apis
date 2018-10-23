import run
import json

bodies = [{
    'clips': [{
        'clip_id': 'c-3G4kwkd7PPCkjpVszoHjVd',
    } , {
        'stream_id': 311038404,
        'time_in': 1593.699742,
        'time_out': 1598.455016,
    }],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

