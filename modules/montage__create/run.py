import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.dynamodb.montage_clip
import ts_aws.mediaconvert.montage
import ts_logger
import ts_model.Exception
import ts_model.Montage
import ts_model.MontageClip
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
        clip_ids = body['clip_ids']

        clips = ts_aws.dynamodb.clip.get_clips(clip_ids)
        if not all(c._status == ts_model.Status.READY for c in clips):
            raise ts_model.Exception(ts_model.Exception.CLIPS__NOT_READY)

        # create montage
        montage_id = f"m-{shortuuid.uuid()}"
        montage = ts_model.Montage(
            montage_id=montage_id,
            _status=ts_model.Status.INITIALIZING
        )

        # create montage_clips
        montage_clips = []
        for index, clips in enumerate(clips):
            montage_clip = ts_model.MontageClip(
                montage_id=montage.montage_id,
                clip_id=clips.clip_id,
                clip_order=index,
                media_key=clips.media_key,
            )
            montage_clips.append(montage_clip)

        ts_aws.mediaconvert.montage.create(montage, montage_clips)
        ts_aws.dynamodb.montage_clip.save_montage_clips(montage_clips)
        ts_aws.dynamodb.montage.save_montage(montage)

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
