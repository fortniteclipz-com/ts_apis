import ts_aws.dynamodb.clip
import ts_aws.dynamodb.stream
import ts_aws.sqs.clip
import ts_aws.sqs.stream__initialize
import ts_logger
import ts_model.Clip
import ts_model.Exception
import ts_model.Status
import ts_model.Stream

import json
import shortuuid
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        body = json.loads(event['body'])
        logger.info("body", body=body)
        stream_id = body['stream_id']
        time_in = body['time_in']
        time_out = body['time_out']

        # get/initialize stream
        try:
            stream = ts_aws.dynamodb.stream.get_stream(stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM__NOT_EXIST:
                logger.error("warn", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
                stream = ts_model.Stream(
                    stream_id=stream_id,
                )
                ts_aws.dynamodb.stream.save_stream(stream)

        if stream._status_initialize == ts_model.Status.NONE:
            stream._status_initialize = ts_model.Status.INITIALIZING
            ts_aws.dynamodb.stream.save_stream(stream)
            ts_aws.sqs.stream__initialize.send_message({
                'stream_id': stream.stream_id,
            })

        # create clip
        clip_id = f"c-{shortuuid.uuid()}"
        clip = ts_model.Clip(
            clip_id=clip_id,
            stream_id=stream_id,
            time_in=time_in,
            time_out=time_out,
            _status=ts_model.Status.INITIALIZING,
        )

        # save clip
        ts_aws.dynamodb.clip.save_clip(clip)

        # send job to clip
        ts_aws.sqs.clip.send_message({
            'clip_id': clip.clip_id,
        })

        logger.info("success", clip=clip)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'clip': clip,
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
