import run

parameters = [{
    'limit': '20',
}]

for params in parameters:
    event = {'queryStringParameters': params}
    run.run(event, {})

