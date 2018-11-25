import ts_aws.rds.clip
import ts_aws.rds.montage
import ts_aws.rds.montage_clip
import ts_aws.rds.stream
import ts_aws.sqs.clip
import ts_aws.sqs.montage
import ts_aws.sqs.stream__initialize
import ts_logger
import ts_model.Montage
import ts_model.Status

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

        try:
            stream = ts_aws.rds.stream.get_stream(stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM__NOT_EXIST:
                logger.error("warn", _module=f"{e.__class__.__module__}", _class=f"{e.__class__.__name__}", _message=str(e), traceback=''.join(traceback.format_exc()))
                stream = ts_model.Stream(
                    stream_id=stream_id,
                )

        if stream._status_initialize == ts_model.Status.NONE:
            stream._status_initialize = ts_model.Status.INITIALIZING
            ts_aws.rds.stream.save_stream(stream)
            ts_aws.sqs.stream__initialize.send_message({
                'stream_id': stream.stream_id,
            })

        montage_id = f"m-{shortuuid.uuid()}"
        montage_clips = [];
        montage_duration = 0;
        def get_clips(arg):
            (index, _clip) = arg
            nonlocal montage_duration
            time_in = _clip['time_in']
            time_out = _clip['time_out']

            clip_id = f"c-{shortuuid.uuid()}"
            montage_duration += time_out - time_in

            clip = ts_model.Clip(
                clip_id=clip_id,
                user_id=user_id,
                stream_id=stream.stream_id,
                time_in=time_in,
                time_out=time_out,
                _status=ts_model.Status.INITIALIZING,
            )
            montage_clip = ts_model.MontageClip(
                montage_id=montage_id,
                clip_id=clip_id,
                clip_order=index + 1,
            )

            return (clip, montage_clip)

        [clips, montage_clips] = zip(*list(map(get_clips, enumerate(clips))))
        ts_aws.rds.clip.save_clips(clips)

        def send_clips(_clip):
            ts_aws.sqs.clip.send_message({
                'clip_id': _clip.clip_id,
            })
            return _clip.clip_id

        clip_ids = list(map(send_clips, clips))
        montage = ts_model.Montage(
            montage_id=montage_id,
            user_id=user_id,
            stream_id=stream.stream_id,
            streamer=stream.streamer,
            duration=montage_duration,
            clips=len(clip_ids),
            _status=ts_model.Status.INITIALIZING,
        )

        ts_aws.rds.montage.save_montage(montage)
        ts_aws.rds.montage_clip.save_montage_clips(montage_clips)
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
