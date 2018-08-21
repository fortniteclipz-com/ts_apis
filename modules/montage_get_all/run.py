import ts_aws.dynamodb.montage_clips
import ts_logger

logger = ts_logger.get(__name__)

def run(event, context):
    logger.info("start", event=event, context=context)
    montages = ts_aws.dynamodb.montage.get_all_montages()

    for m in montages:
        montage_clips = ts_aws.dynamodb.montage_clips.get_montage_clips(m.montage_id)
        m.clip_ids = list(map(lambda mc: mc.clip_id, montage_clips))

    logger.info("done", response=response)
    return response
