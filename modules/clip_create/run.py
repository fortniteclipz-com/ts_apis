import ts_aws.dynamodb.clip
import ts_aws.sqs.clip
import ts_logger
import ts_model.Clip
import ts_model.Status

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
    clip = ts_model.Clip(
        clip_id=clip_id,
        stream_id=stream_id,
        time_in=clip_time_in,
        time_out=clip_time_out,
        _status=ts_model.Status.INITIALIZING
    )
    ts_aws.dynamodb.clip.save_clip(clip)

    payload = {
        'clip_id': clip.clip_id,
    }
    ts_aws.sqs.clip.send_message(payload)

    response = clip.clip_id
    logger.info("done", response=response)
    return clip.clip_id

