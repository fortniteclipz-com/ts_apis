import run

parameters = [{
    'stream_id': 310285421,
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

