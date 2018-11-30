import run
import json

parameters = [{
    'stream_id': "335886831",
}]

for p in parameters:
    event = {
        'pathParameters': p,
        'body': json.dumps({
            'game': 'fortnite',
        })
    }
    run.run(event, {})

