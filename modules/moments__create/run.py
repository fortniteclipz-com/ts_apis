import ts_aws.rds.stream
import ts_aws.sqs.stream__analyze
import ts_logger
import ts_model.Exception
import ts_model.Status
import ts_model.Stream

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        params = event['pathParameters']
        logger.info("params", params=params)
        stream_id = params['stream_id']
        body = json.loads(event['body'])
        logger.info("body", body=body)
        game = body['game']

        if game != 'fortnite':
            raise ts_model.Exception(ts_model.Exception.STREAM_MOMENTS__GAME_NOT_SUPPORTED)

        try:
            stream = ts_aws.rds.stream.get_stream(stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM__NOT_EXIST:
                logger.error("warn", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
                stream = ts_model.Stream(
                    stream_id=stream_id,
                )

        if stream._status_analyze == ts_model.Status.DONE:
            raise ts_model.Exception(ts_model.Exception.STREAM__STATUS_ANALYZE_DONE)

        if stream._status_analyze == ts_model.Status.WORKING:
            raise ts_model.Exception(ts_model.Exception.STREAM__STATUS_ANALYZE_WORKING)

        stream.game = game
        stream._status_analyze = ts_model.Status.WORKING
        ts_aws.rds.stream.save_stream(stream)
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
