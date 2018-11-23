import run

parameters = [{
    'stream_id': "335886831",
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

