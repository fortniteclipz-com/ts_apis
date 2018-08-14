import ts_aws.dynamodb.montage
import ts_logger

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        montages = ts_aws.dynamodb.montage.get_all_montages()
        montage_ids = list(map(lambda m: m.montage_id, montages))
        montages_clips = ts_aws.dynamodb.montage.get_montages_clips(montage_ids)

        for m in montages:
            m.montage_clips = []
            for mc in montages_clips:
                if mc.montage_id == m.montage_id:
                    m.montage_clips.append(mc)
        for m in montages:
            m.montage_clips.sort(key=lambda mc: mc.clip_order)

        def serialize(m):
            m.clip_ids = list(map(lambda mc: mc.clip_id, m.montage_clips))
            del m.montage_clips
            return m.__dict__
        response = list(map(serialize, montages))

        logger.info("done", response=response)
        return response

    except Exception as e:
        logger.error("error", error=e)
        raise Exception('Invalid Request')
