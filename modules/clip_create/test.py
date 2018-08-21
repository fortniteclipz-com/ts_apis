import run

data = {
	'stream_id': 285219394,
	'time_in': 6,
	'time_out': 23,
}
event = {'body': data}
run.run(event, {})

