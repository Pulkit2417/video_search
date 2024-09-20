from django.shortcuts import render, redirect, reverse
from django.http import HttpResponseBadRequest
from .models import Video, Subtitle
from .forms import VideoUploadForm
import subprocess
import json
from django.conf import settings
import os
import re

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save()
            extract_subtitles(video)
            return redirect('video_list')
    else:
        form = VideoUploadForm()
    return render(request, 'upload_video.html', {'form': form})

def video_list(request):
    videos = Video.objects.all()
    return render(request, 'video_list.html', {'videos': videos})

def extract_subtitles(video):
    # Path to the video file
    video_path = video.file.path

    # Get all subtitle streams using ffmpeg
    result = subprocess.run(
        ['ffmpeg', '-i', video_path],
        stderr=subprocess.PIPE, text=True
    )
    # Updated regex to capture subtitle stream and language (if available)
    subtitle_lines = re.findall(r"Stream #0:(\d+)\((\w+)\): Subtitle:", result.stderr)

    for stream_index, language in subtitle_lines:
        vtt_output_path = os.path.join('subtitles',f"{video.id}_{language}_subtitles.vtt")
        print(f"VTT Output Path: {vtt_output_path}")
        # Use ffmpeg to extract subtitles in WebVTT format
        subprocess.run([
            'ffmpeg',
            '-i', video_path,
            '-map', f'0:{stream_index}',
            '-c:s', 'webvtt',  # Extract the first subtitle stream (adjust as necessary)
            os.path.join(settings.MEDIA_ROOT,vtt_output_path)
        ], stdout=subprocess.PIPE, text=True, encoding='utf-8').stdout
        print(vtt_output_path)

        # Open and parse the VTT file
        with open(os.path.join(settings.MEDIA_ROOT,vtt_output_path), 'r', encoding='utf-8') as file:
            subtitles_data = parse_vtt(file.read())
        
        # Save subtitles to the database
        for subtitle_data in subtitles_data:
            Subtitle.objects.create(
                video=video,
                language=language,
                start_time=subtitle_data['start_time'],
                end_time=subtitle_data['end_time'],
                phrase=subtitle_data['phrase'],
                file=vtt_output_path,
            )

def parse_vtt(vtt_content):
    subtitles = []
    for block in vtt_content.split('\n\n'):
        lines = block.split('\n')
        if len(lines) >= 2:
            time_range = lines[0]
            start_time, end_time = time_range.split(' --> ')
            phrase = ' '.join(lines[1:])
            subtitles.append({
                'start_time': start_time.strip(),
                'end_time': end_time.strip(),
                'phrase': phrase.strip(),
            })
    return subtitles

def time_to_seconds(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return int(hours) * 3600 + int(minutes) * 60 + float(seconds)
    elif len(parts) == 2:
        minutes, seconds = parts
        return int(minutes) * 60 + float(seconds)
    return float(parts[0])

def format_time_to_hhmmss(time_str):
    parts = time_str.split(':')
    if len(parts) == 3:
        # Time is already in HH:MM:SS format
        return time_str
    elif len(parts) == 2:
        # Convert MM:SS to HH:MM:SS
        return f"00:{time_str}"
    elif len(parts) == 1:
        # If only seconds are provided, convert to HH:MM:SS
        seconds = int(parts[0])
        return f"{seconds // 3600:02}:{(seconds % 3600) // 60:02}:{seconds % 60:02}"
    return "00:00:00"  # Default in case of an invalid time


# Assuming this is inside your search_subtitles view
def search_subtitles(request, video_id):
    video = Video.objects.get(id=video_id)
    query = request.GET.get('q', '')
    
    # Search the subtitles for the matching phrase
    result = Subtitle.objects.filter(video=video, phrase__icontains=query).first()

    if result:
        start_time = result.start_time
        #start_time = format_time_to_hhmmss(start_time)
        start_time_seconds = round(time_to_seconds(start_time))  # Convert start_time to seconds
        # Redirect to the video playback with the correct start time
        return redirect(reverse('video_play', args=[video.id]) + f'?t={start_time_seconds}')
    
    # If no result, render the template with a message
    return render(request, 'search_results.html', {
        'video': video,
        'query': query,
        'message': 'No subtitles found for this query.'
    })

def play_video(request, video_id):
    video = Video.objects.get(id=video_id)
    subtitles = Subtitle.objects.filter(video=video).distinct('language')
    start_time = request.GET.get('t')
    print(f"Start time (t parameter): {start_time}")
    return render(request, 'play_video.html', {'video': video,'subtitles':subtitles, 'start_time': start_time})
