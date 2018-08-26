import ts_aws.dynamodb.clip
import ts_logger

logger = ts_logger.get(__name__)

def run(event, context):
    logger.info("start", event=event, context=context)
    clips = ts_aws.dynamodb.clip.get_all_clips()

    response = list(map(lambda c: c.__dict__, clips))
    logger.info("success", response=response)
    return response
