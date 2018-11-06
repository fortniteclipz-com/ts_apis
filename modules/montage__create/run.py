import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.dynamodb.stream
import ts_aws.dynamodb.user_montage
import ts_aws.sqs.clip
import ts_aws.sqs.montage
import ts_aws.sqs.stream__initialize
import ts_logger
import ts_model.Montage
import ts_model.Status
import ts_model.UserMontage

import datetime
import json
import shortuuid
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']
        body = json.loads(event['body'])
        logger.info("body", body=body)
        stream_id = body['stream_id']
        clips = body['clips']
        created = datetime.datetime.utcnow().isoformat()

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

        montage_duration = 0;
        def get_clips(_clip):
            nonlocal montage_duration
            time_in = _clip['time_in']
            time_out = _clip['time_out']

            clip_id = f"c-{shortuuid.uuid()}"
            clip = ts_model.Clip(
                clip_id=clip_id,
                stream_id=stream.stream_id,
                time_in=time_in,
                time_out=time_out,
                _status=ts_model.Status.INITIALIZING,
            )

            montage_duration += clip.time_out - clip.time_in
            return clip

        clips = list(map(get_clips, clips))

        ts_aws.dynamodb.clip.save_clips(clips)

        def create_clips(_clip):
            ts_aws.sqs.clip.send_message({
                'clip_id': _clip.clip_id,
            })
            return _clip.clip_id

        clip_ids = list(map(create_clips, clips))

        montage_id = f"m-{shortuuid.uuid()}"
        montage = ts_model.Montage(
            montage_id=montage_id,
            stream_id=stream.stream_id,
            stream_user=stream.user,
            duration=montage_duration,
            clip_ids=clip_ids,
            _status=ts_model.Status.INITIALIZING
        )
        user_montage = ts_model.UserMontage(
            user_id=user_id,
            montage_id=montage.montage_id,
            created=created,
        )

        ts_aws.dynamodb.montage.save_montage(montage)
        ts_aws.dynamodb.user_montage.save_user_montage(user_montage)

        ts_aws.sqs.montage.send_message({
            'montage_id': montage.montage_id,
        })

        logger.info("success", montage=montage)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'montage': montage,
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
