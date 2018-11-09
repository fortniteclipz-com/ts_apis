import ts_aws.dynamodb.recent
import ts_aws.dynamodb.stream
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        recent_stream = ts_aws.dynamodb.recent.get_stream()
        streams = []
        if len(recent_stream.media_ids):
            streams = ts_aws.dynamodb.stream.get_streams(recent_stream.media_ids)
            streams.sort(key=lambda s: recent_stream.media_ids.index(s.stream_id))
        logger.info("success", streams=streams)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'streams': streams,
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
