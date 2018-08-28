import run
import json

bodies = [{
    'stream_id': 285219394,
    'time_in': 6,
    'time_out': 23,
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

