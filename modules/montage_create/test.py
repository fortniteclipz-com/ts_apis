import run
import json

data = {
    'clip_ids': [
        "c-gJdUyL7eTVUowwxKoPKQE9",
    ],
}
event = {'body': json.dumps(data)}
run.run(event, {})

