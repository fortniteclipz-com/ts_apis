import run
import json

bodies = [{
    'clip_ids': [
        "c-qCuPKxsMpYPMPqjEzUJRsV",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

