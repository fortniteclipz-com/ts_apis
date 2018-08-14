import ts_aws.dynamodb.montage
import ts_aws.sqs
import ts_logger

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        body = event['body']
        logger.info("body", body=body)
        clip_ids = body['clip_ids']

        montage = ts_aws.dynamodb.montage.Montage()
        montage = ts_aws.dynamodb.montage.save_montage(montage)
        logger.info("montage created", montage=montage.__dict__)

        montage_clips = []
        for index, clip_id in enumerate(clip_ids):
            montage_clip = ts_aws.dynamodb.montage.MontageClip(
                montage_id=montage.montage_id,
                clip_id=clip_id,
                clip_order=index,
            )
            montage_clips.append(montage_clip)
        montage_clips = ts_aws.dynamodb.montage.save_montage_clips(montage_clips)

        payload = {'montage_id': montage.montage_id}
        logger.info("pushing to stream_montage sqs", payload=payload)
        ts_aws.sqs.send_clips_montage(payload)

        logger.info("done")
        return montage.montage_id

    except Exception as e:
        logger.error("error", error=e)
        raise Exception('Invalid Request')
