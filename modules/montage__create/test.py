import run
import json

bodies = [{
    'clip_ids': [
        "c-b2qtQ6BK8FTdAFqb8vNwDY",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

