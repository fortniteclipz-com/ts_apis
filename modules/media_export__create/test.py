import run
import json

bodies = [{
    'media_type': "",
    'media_id': "",
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

