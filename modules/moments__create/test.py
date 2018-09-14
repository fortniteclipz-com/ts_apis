import run

parameters = [{
    'stream_id': 285219394,
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

