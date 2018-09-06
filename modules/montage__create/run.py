import ts_aws.dynamodb.montage
import ts_aws.sqs.montage
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
        clip_ids = body['clip_ids']

        # create montage
        montage_id = f"m-{shortuuid.uuid()}"
        montage = ts_model.Montage(
            montage_id=montage_id,
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
