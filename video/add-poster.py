#!/usr/bin/env python

import ffmpeg

time = 62
file = '/Users/zhangz/Downloads/opera.mp4'
probe = ffmpeg.probe(file)
video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)
width = int(video_stream['width'])
height = int(video_stream['height'])
frames = int(video_stream['nb_frames'])
r_frame = (video_stream['r_frame_rate']).split('/')
fps = float(r_frame[0])/float(r_frame[1])
frame = int(time*fps)

audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)

image, _ = (
    ffmpeg
        .input(file)
        .filter('select', 'gte(n,{})'.format(frame))
        .output('pipe:', vframes=1, format='image2', vcodec='mjpeg')
        .run(capture_stdout=True)
)

