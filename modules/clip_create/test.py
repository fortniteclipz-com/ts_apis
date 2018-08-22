import run

datas = [{
    'stream_id': 285219394,
    'time_in': 6,
    'time_out': 23,
}, {
    'stream_id': 285219394,
    'time_in': 50,
    'time_out': 75,
}]

for data in datas:
    event = {'body': data}
    run.run(event, {})

