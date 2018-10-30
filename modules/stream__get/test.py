import run

parameters = [{
    'stream_id': "308963791",
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

