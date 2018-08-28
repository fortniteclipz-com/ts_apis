import run
import json

bodies = [{
    'media_type': "clip",
    'media_id': "c-rdMaVaUnwWJ9xHgSnA9EJK",
}]

for body in bodies:
    event = {'body': json.dumps(body)}
    run.run(event, {})

