import ts_aws.dynamodb.clip
import ts_aws.dynamodb.montage
import ts_aws.dynamodb.montage_clip
import ts_aws.s3
import ts_file
import ts_logger
import ts_media
import ts_model.Exception
import ts_model.Montage
import ts_model.MontageClip
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
        montage = ts_model.Montage(montage_id=montage_id)

        # create montage_clips
        montage_clips = []
        for index, clip_id in enumerate(clip_ids):
            montage_clip = ts_model.MontageClip(
                montage_id=montage.montage_id,
                clip_id=clip_id,
                clip_order=index,
            )
            montage_clips.append(montage_clip)

        # check clips
        clip_ids = list(map(lambda mc: mc.clip_id, montage_clips))
        clips = ts_aws.dynamodb.clip.get_clips(clip_ids)
        if not all(c._status == ts_model.Status.READY for c in clips):
            raise ts_model.Exception(ts_model.Exception.CLIPS__NOT_READY)

        # get clips_segments
        clips_segments = ts_aws.dynamodb.clip.get_clips_clip_segments(clip_ids)
        clip_id = clips_segments[0].clip_id
        for cs in clips_segments:
            if cs.clip_id != clip_id:
                cs.discontinuity = True
                clip_id = cs.clip_id

        # create/upload m3u8
        m3u8_filename_master = f"/tmp/playlist-master.m3u8"
        m3u8_filename_video = f"/tmp/playlist-video.m3u8"
        m3u8_filename_audio = f"/tmp/playlist-audio.m3u8"
        ts_media.create_m3u8(clips_segments, m3u8_filename_master, m3u8_filename_video, m3u8_filename_audio)
        m3u8_key_master = f"montages/{montage_id}/playlist-master.m3u8"
        m3u8_key_video = f"montages/{montage_id}/playlist-video.m3u8"
        m3u8_key_audio = f"montages/{montage_id}/playlist-audio.m3u8"
        ts_aws.s3.upload_file(m3u8_filename_master, m3u8_key_master)
        ts_aws.s3.upload_file(m3u8_filename_video, m3u8_key_video)
        ts_aws.s3.upload_file(m3u8_filename_audio, m3u8_key_audio)
        ts_file.delete(m3u8_filename_master)
        ts_file.delete(m3u8_filename_video)
        ts_file.delete(m3u8_filename_audio)

        # save montage and montage_clips
        montage.key_playlist_master = m3u8_key_master
        montage.key_playlist_video = m3u8_key_video
        montage.key_playlist_audio = m3u8_key_audio
        ts_aws.dynamodb.montage_clip.save_montage_clips(montage_clips)
        ts_aws.dynamodb.montage.save_montage(montage)

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
