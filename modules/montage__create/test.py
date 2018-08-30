import run
import json

bodies = [{
    'clip_ids': [
        "c-NibQGRzhJ6ZeKktGezP4Cg",
        "c-ikKbrkvAY6UZpdenP4S8b6",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

