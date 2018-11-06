import run

parameters = [{
    'limit': "50",
}]

for params in parameters:
    event = {'queryStringParameters': params}
    run.run(event, {})

