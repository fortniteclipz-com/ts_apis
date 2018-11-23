import run

event = {'requestContext': {'authorizer': {'claims': {'cognito:username': 'development-test-username'}}}}
run.run(event, {})
