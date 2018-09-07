import ts_aws.dynamodb.stream
import ts_aws.dynamodb.stream_event
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        params = event.get('pathParameters') or {}
        logger.info("params", params=params)
        stream_id = int(params.get('stream_id'))

        stream = ts_aws.dynamodb.stream.get_stream(stream_id)
        stream_events = ts_aws.dynamodb.stream_event.get_stream_events(stream_id)

        logger.info("success", stream=stream, stream_events=stream_events)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'stream': stream,
                'stream_events': stream_events,

            }),
        }

    except Exception as e:
        logger.error("error", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'error': f"{e.__class__.__name__}: {str(e)}",
            }),
        }
