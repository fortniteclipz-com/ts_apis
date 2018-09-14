import ts_aws.dynamodb.stream
import ts_aws.dynamodb.stream_moment
import ts_logger
import ts_model.Exception

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
        try:
            stream_moments = ts_aws.dynamodb.stream_moment.get_stream_moments(stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM_SEGMENTS__NOT_EXIST:
                stream_moments = []

        logger.info("success", stream=stream, stream_moments=stream_moments)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'stream': stream,
                'stream_moments': stream_moments,
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
