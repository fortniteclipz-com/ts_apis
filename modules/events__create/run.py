import ts_aws.sqs.stream__analyze
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        body = json.loads(event['body'])
        logger.info("body", body=body)
        stream_id = body['stream_id']

        # get/initialize stream
        try:
            stream = ts_aws.dynamodb.stream.get_stream(stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM__NOT_EXIST:
                logger.error("warn", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
                stream = ts_model.Stream(
                    stream_id=stream_id,
                    _status_initialize=ts_model.Status.INITIALIZING,
                )
                ts_aws.dynamodb.stream.save_stream(stream)
                ts_aws.sqs.stream_initialize.send_message({
                    'stream_id': stream_id,
                })

        # send job to stream__analyze
        stream._status_analyze = ts_model.Status.INITIALIZING
        ts_aws.dynamodb.stream.save_stream(stream)
        ts_aws.sqs.stream__analyze.send_message({
            'stream_id': stream.stream_id,
        })

        logger.info("success", stream=stream)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'stream': stream,
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
