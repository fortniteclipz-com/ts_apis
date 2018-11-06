import run

event = {'requestContext': {'authorizer': {'claims': {'cognito:username': '8a8ea1bd-8fa5-44db-b319-34db17ae3ef5'}}}}
run.run(event, {})
