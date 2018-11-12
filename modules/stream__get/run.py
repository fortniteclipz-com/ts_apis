import ts_aws.dynamodb.stream
import ts_aws.dynamodb.stream_moment
import ts_aws.dynamodb.stream_segment
import ts_logger
import ts_model.Exception

import json
import traceback

logger = ts_logger.get(__name__)

def run(event, context):
    try:
        logger.info("start", event=event, context=context)
        params = event['pathParameters']
        logger.info("params", params=params)
        stream_id = params['stream_id']

        stream = ts_aws.dynamodb.stream.get_stream(stream_id)
        try:
            stream_moments = ts_aws.dynamodb.stream_moment.get_stream_moments(stream.stream_id)
        except ts_model.Exception as e:
            if e.code == ts_model.Exception.STREAM_MOMENTS__NOT_EXIST:
                stream_moments = []

        if stream._status_analyze == ts_model.Status.INITIALIZING:
            try:
                stream_segments = ts_aws.dynamodb.stream_segment.get_stream_segments(stream.stream_id)
            except ts_model.Exception as e:
                if e.code == ts_model.Exception.STREAM_MOMENTS__NOT_EXIST:
                    stream_segments = []

            downloaded_stream_segments = list(filter(lambda ss: ss._status_download == ts_model.Status.READY, stream_segments))
            analyzed_stream_segments = list(filter(lambda ss: ss._status_analyze == ts_model.Status.READY, stream_segments))
            stream._status_analyze_percentage = (len(downloaded_stream_segments) + len(analyzed_stream_segments)) / (len(stream_segments) * 2) * 100
            stream._status_analyze_percentage = 99 if stream._status_analyze_percentage > 99 else stream._status_analyze_percentage

        logger.info("success", stream=stream, stream_moments=stream_moments)
        return {
            'statusCode': 200,
            'headers': {
                "Access-Control-Allow-Origin" : "*",
            },
            'body': json.dumps({
                'stream': stream,
                'stream_moments': stream_moments,
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
