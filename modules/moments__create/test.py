import run
import json

parameters = [{
    'stream_id': "335886831",
}]

for params in parameters:
    event = {
        'pathParameters': params,
        'body': json.dumps({
            'game': 'fortnite',
        })
    }
    run.run(event, {})

