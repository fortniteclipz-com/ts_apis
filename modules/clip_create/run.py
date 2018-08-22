import ts_aws.dynamodb
import ts_aws.dynamodb.clip
import ts_aws.sqs
import ts_logger

import shortuuid

logger = ts_logger.get(__name__)

def run(event, context):
    logger.info("start", event=event, context=context)
    body = event['body']
    logger.info("body", body=body)
    stream_id = body['stream_id']
    clip_time_in = body['time_in']
    clip_time_out = body['time_out']

    clip_id = f"c-{shortuuid.uuid()}"
    clip = ts_aws.dynamodb.clip.Clip(
        clip_id=clip_id,
        stream_id=stream_id,
        time_in=clip_time_in,
        time_out=clip_time_out,
        _status=ts_aws.dynamodb.Status.INITIALIZING
    )
    ts_aws.dynamodb.clip.save_clip(clip)
    logger.info("clip created", clip=clip.__dict__)

    payload = {
        'clip_id': clip.clip_id,
    }
    logger.info("pushing to stream_clip sqs", payload=payload)
    ts_aws.sqs.send_stream_clip(payload)

    logger.info("done")
    return clip.clip_id

