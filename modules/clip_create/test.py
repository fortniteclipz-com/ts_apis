import run
import json

datas = [{
    'stream_id': 285219394,
    'time_in': 6,
    'time_out': 23,
}]

for data in datas:
    event = {'body': json.dumps(data)}
    run.run(event, {})

