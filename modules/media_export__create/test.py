import run
import json

datas = [{
    'media_type': "",
    'media_id': "",
}]

for data in datas:
    event = {'body': json.dumps(data)}
    run.run(event, {})

