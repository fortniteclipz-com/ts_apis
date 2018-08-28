import run
import json

bodies = [{
    'clip_ids': [
        "c-gJdUyL7eTVUowwxKoPKQE9",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

