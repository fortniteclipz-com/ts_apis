import ts_aws.dynamodb.clip
import ts_aws.dynamodb.clip_segment
import ts_aws.dynamodb.montage
import ts_aws.dynamodb.montage_clip
import ts_aws.s3
import ts_file
import ts_logger
import ts_media

import shortuuid

logger = ts_logger.get(__name__)

def run(event, context):
    logger.info("start", event=event, context=context)
    body = event['body']
    logger.info("body", body=body)
    clip_ids = body['clip_ids']

    montage_id = f"m-{shortuuid.uuid()}"
    montage = ts_aws.dynamodb.montage.Montage(montage_id=montage_id)
    logger.set(montage=montage.__dict__).logger.info("montage")

    montage_clips = []
    for index, clip_id in enumerate(clip_ids):
        montage_clip = ts_aws.dynamodb.montage_clip.MontageClip(
            montage_id=montage.montage_id,
            clip_id=clip_id,
            clip_order=index,
        )
        montage_clips.append(montage_clip)
    logger.info("montage_clips", montage_clips_length=len(montage_clips))

    clip_ids = list(map(lambda mc: mc.clip_id, montage_clips))
    clips = ts_aws.dynamodb.clip.get_clips(clip_ids)
    if not all(c.is_init() for c in clips):
        logger.error("clips not ready to montage")
        raise Exception("Not all clips processed yet")

    clips_segments = ts_aws.dynamodb.clip_segment.get_clips_segments(clip_ids)
    logger.info("clips_segments", clips_segments_length=len(clips_segments))

    clip_id = clips_segments[0].clip_id
    for cs in clips_segments:
        if cs.clip_id != clip_id:
            cs.discontinuity = True
            clip_id = cs.clip_id

    # creating/uploading m3u8
    logger.info("creating/uploading m3u8")
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

    logger.info("saving montage and montage_clips")
    montage.key_playlist_master = m3u8_key_master
    montage.key_playlist_video = m3u8_key_video
    montage.key_playlist_audio = m3u8_key_audio
    ts_aws.dynamodb.montage.save_montage(montage)
    ts_aws.dynamodb.montage_clip.save_montage_clips(montage_clips)

    logger.info("done")
    return montage.montage_id
