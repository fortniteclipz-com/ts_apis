import ts_aws.mediaconvert
import ts_logger
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

        ts_aws.mediaconvert.create_media_export(media_type, media_id)

        logger.info("success")
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'media_type': media_type,
                'media_id': media_id,
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
