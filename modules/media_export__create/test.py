import run
import json

bodies = [{
    'media_type': "clip",
    'media_id': "c-zbFvt88cty9VhkpKqHVLDo",
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

