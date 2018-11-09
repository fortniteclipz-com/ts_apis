import ts_aws.dynamodb.montage
import ts_aws.dynamodb.recent
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        recent_montage = ts_aws.dynamodb.recent.get_montage()
        montages = []
        if len(recent_montage.media_ids):
            montages = ts_aws.dynamodb.montage.get_montages(recent_montage.media_ids)
            montages.sort(key=lambda m: recent_montage.media_ids.index(m.montage_id))
        logger.info("success", montages=montages)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'montages': montages,
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
