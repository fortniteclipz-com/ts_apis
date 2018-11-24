import run

parameters = [{
    'stream_id': "328002305",
}]

for params in parameters:
    event = {'pathParameters': params}
    run.run(event, {})

