import ts_aws.dynamodb.montage
import ts_aws.dynamodb.montage_clip
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        montages = ts_aws.dynamodb.montage.get_all_montages()

        for m in montages:
            montage_clips = ts_aws.dynamodb.montage_clip.get_montage_clips(m.montage_id)
            m.clip_ids = list(map(lambda mc: mc.clip_id, montage_clips))

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
