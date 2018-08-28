import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.mediaconvert
import ts_logger
import ts_model.Exception
import ts_model.Status

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        body = json.loads(event['body'])
        logger.info("body", body=body)
        media_type = body['media_type']
        media_id = body['media_id']

        if media_type == "clip":
            media = ts_aws.dynamodb.clip.get_clip(media_id)
        elif media_type == "montage":
            media = ts_aws.dynamodb.montage.get_montage(media_id)
        else:
            raise ts_model.Exception(ts_model.Exception.MEDIA_EXPORT__INVALID_MEDIA_TYPE)

        if media._status != ts_model.Status.READY:
            raise ts_model.Exception(ts_model.Exception.MEDIA__NOT_READY)
        if media._status_export == ts_model.Status.READY:
            raise ts_model.Exception(ts_model.Exception.MEDIA_EXPORT__ALREADY_PROCESSED)
        if media._status_export == ts_model.Status.INITIALIZING:
            raise ts_model.Exception(ts_model.Exception.MEDIA_EXPORT__ALREADY_INITIALIZING)

        ts_aws.mediaconvert.create_media_export(media_type, media_id)
        media._status_export = ts_model.Status.INITIALIZING

        if media_type == "clip":
            ts_aws.dynamodb.clip.save_clip(media)
        elif media_type == "montage":
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
