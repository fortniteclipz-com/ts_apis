import run

parameters = [{
    'stream_id': "328002305",
}]

for p in parameters:
    event = {'pathParameters': p}
    run.run(event, {})

