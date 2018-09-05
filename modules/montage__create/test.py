import run
import json

bodies = [{
    'clip_ids': [
        "c-7khkE2rBch69oDtrAZJSXd",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

