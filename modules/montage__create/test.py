import run
import json

bodies = [{
    'clip_ids': [
        "c-Lg8SpMbfuH8LcvEUeCYbXi",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

