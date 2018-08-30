import run
import json

bodies = [{
    'montage_id': "m-PjBRKetG9S43nsMhNgxU6b",
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

