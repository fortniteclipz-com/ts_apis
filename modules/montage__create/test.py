import run
import json

bodies = [{
    'clip_ids': [
        "c-jd8fbHXJyTmGAFz8SepSDm",
    ],
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

