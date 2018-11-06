import run

parameters = [{
    'stream_id': "308990189",
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

