import ts_aws.dynamodb.montage
import ts_aws.dynamodb.user_montage
import ts_logger

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        user_id = event['requestContext']['authorizer']['claims']['cognito:username']

        user_montages = ts_aws.dynamodb.user_montage.get_user_montages(user_id)
        montage_ids = list(map(lambda um: um.montage_id, user_montages))
        montages = []
        if len(montage_ids):
            montages = ts_aws.dynamodb.montage.get_montages(montage_ids)
            montages.sort(key=lambda m: montage_ids.index(m.montage_id))

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
