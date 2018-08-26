import ts_aws.dynamodb.clip
import ts_aws.sqs.clip
import ts_logger
import ts_model.Clip
import ts_model.Status

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
        ime_out = body['time_out']

        # create clip
        clip_id = f"c-{shortuuid.uuid()}"
        clip = ts_model.Clip(
            clip_id=clip_id,
            stream_id=stream_id,
            time_in=time_in,
            time_out=ime_out,
            _status=ts_model.Status.INITIALIZING,
        )
        ts_aws.dynamodb.clip.save_clip(clip)

        # send clip job to sqs
        payload = {
            'clip_id': clip.clip_id,
        }
        ts_aws.sqs.clip.send_message(payload)

        logger.info("success", clip=clip)
        return {
            'statusCode': 200,
            'body': json.dumps({
                'clip': clip,
            }),
        }

    except Exception as e:
        logger.error("error", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f"{e.__class__.__name__}: {str(e)}",
            }),
        }
