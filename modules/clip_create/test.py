import run

data = {
	'stream_id': 294350186,
	'time_in': 0,
	'time_out': 11,
}
event = {'body': data}
run.run(event, {})

