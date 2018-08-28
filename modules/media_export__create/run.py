import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.mediaconvert
import ts_logger
import ts_model.Clip
import ts_model.Exception
import ts_model.Montage
import ts_model.Status

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        body = json.loads(event['body'])
        logger.info("body", body=body)

        if 'montage_id' in body:
            media_id = body['montage_id']
            media = ts_aws.dynamodb.montage.get_montage(media_id)
            media_type = "montage"
        elif 'clip_id' in body:
            media_id = body['clip_id']
            media = ts_aws.dynamodb.clip.get_clip(media_id)
            media_type = "clip"
        else:
            raise ts_model.Exception(ts_model.Exception.MEDIA__NOT_EXIST)

        if type(media) == ts_model.Clip and media._status != ts_model.Status.READY:
            raise ts_model.Exception(ts_model.Exception.CLIP__NOT_READY)
        if media._status_export == ts_model.Status.READY:
            raise ts_model.Exception(ts_model.Exception.MEDIA__ALREADY_PROCESSED)
        if media._status_export == ts_model.Status.INITIALIZING:
            raise ts_model.Exception(ts_model.Exception.MEDIA__ALREADY_INITIALIZING)

        ts_aws.mediaconvert.create_media_export(media_type, media_id)
        media._status_export = ts_model.Status.INITIALIZING

        if type(media) == ts_model.Clip:
            ts_aws.dynamodb.clip.save_clip(media)
        elif type(media) == ts_model.Montage:
            ts_aws.dynamodb.montage.save_montage(media)

        logger.info("success")
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                media_type: media,
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
