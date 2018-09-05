import run
import json

bodies = [{
    'stream_id': 285219394,
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

