import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.dynamodb.stream
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
        body = json.loads(event['body'])
        logger.info("body", body=body)
        clips = body['clips']

        montage_duration = 0;
        montage_stream_id = None;

        _clip_ids = list(map(lambda c: c['clip_id'], filter(lambda c: True if 'clip_id' in c else False, clips)))
        _clips = []
        if (len(_clip_ids)):
            _clips = ts_aws.dynamodb.clip.get_clips(_clip_ids)

        def get_clip_id(clip):
            nonlocal montage_duration
            nonlocal montage_stream_id
            if 'clip_id' in clip:
                clip = [c for c in _clips if c.clip_id == clip['clip_id']][0]

            else:
                stream_id = clip['stream_id']
                time_in = clip['time_in']
                time_out = clip['time_out']

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

            montage_duration += clip.time_out - clip.time_in
            montage_stream_id = clip.stream_id
            return clip.clip_id

        clip_ids = list(map(get_clip_id, clips))

        # create montage
        montage_id = f"m-{shortuuid.uuid()}"
        montage = ts_model.Montage(
            montage_id=montage_id,
            stream_id=montage_stream_id,
            duration=montage_duration,
            clip_ids=clip_ids,
            _status=ts_model.Status.INITIALIZING
        )

        # save montage
        ts_aws.dynamodb.montage.save_montage(montage)

        # send job to montage
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
