from typing import List, Optional
from pathlib import Path
from tqdm import tqdm
import glob
import mimetypes
import os
import platform
import shutil
import ssl
import subprocess
import tempfile
import urllib
import onnxruntime

import faceswap.globals
from faceswap import wording
from faceswap.vision import detect_fps

TEMP_DIRECTORY_PATH = os.path.join(tempfile.gettempdir(), 'faceswap')
TEMP_OUTPUT_VIDEO_NAME = 'temp.mp4'
TEMP_OUTPUT_AUDIO_NAME = 'temp.mp3'

# monkey patch ssl
if platform.system().lower() == 'darwin':
	ssl._create_default_https_context = ssl._create_unverified_context


def run_ffmpeg(args : List[str]) -> bool:
	commands = [ 'ffmpeg', '-hide_banner', '-loglevel', 'error' ]
	commands.extend(args)
	try:
		subprocess.run(commands, stderr = subprocess.PIPE, check = True)
		return True
	except subprocess.CalledProcessError:
		return False


def open_ffmpeg(args : List[str]) -> subprocess.Popen[bytes]:
	commands = [ 'ffmpeg', '-hide_banner', '-loglevel', 'error' ]
	commands.extend(args)
	return subprocess.Popen(commands, stdin = subprocess.PIPE)


def extract_frames(target_path : str, fps : float) -> bool:
	temp_frame_compression = round(31 - (faceswap.globals.temp_frame_quality * 0.31))
	trim_frame_start = faceswap.globals.trim_frame_start
	trim_frame_end = faceswap.globals.trim_frame_end
	temp_frames_pattern = get_temp_frames_pattern(target_path)
	commands = [ '-hwaccel', 'auto', '-i', target_path, '-q:v', str(temp_frame_compression), '-pix_fmt', 'rgb24' ]
	if trim_frame_start is not None and trim_frame_end is not None:
		commands.extend([ '-vf', 'trim=start_frame=' + str(trim_frame_start) + ':end_frame=' + str(trim_frame_end) + ',fps=' + str(fps) ])
	elif trim_frame_start is not None:
		commands.extend([ '-vf', 'trim=start_frame=' + str(trim_frame_start) + ',fps=' + str(fps) ])
	elif trim_frame_end is not None:
		commands.extend([ '-vf', 'trim=end_frame=' + str(trim_frame_end) + ',fps=' + str(fps) ])
	else:
		commands.extend([ '-vf', 'fps=' + str(fps) ])
	commands.extend([ '-vsync', '0', temp_frames_pattern ])
	return run_ffmpeg(commands)


def compress_image(output_path : str) -> bool:
	output_image_compression = round(31 - (faceswap.globals.output_image_quality * 0.31))
	commands = [ '-hwaccel', 'auto', '-i', output_path, '-q:v', str(output_image_compression), '-y', output_path ]
	return run_ffmpeg(commands)


def merge_video(target_path : str, fps : float) -> bool:
	temp_output_video_path = get_temp_output_video_path(target_path)
	temp_frames_pattern = get_temp_frames_pattern(target_path)
	commands = [ '-hwaccel', 'auto', '-r', str(fps), '-i', temp_frames_pattern, '-c:v', faceswap.globals.output_video_encoder ]
	if faceswap.globals.output_video_encoder in [ 'libx264', 'libx265' ]:
		output_video_compression = round(51 - (faceswap.globals.output_video_quality * 0.5))
		commands.extend([ '-crf', str(output_video_compression) ])
	if faceswap.globals.output_video_encoder in [ 'libvpx-vp9' ]:
		output_video_compression = round(63 - (faceswap.globals.output_video_quality * 0.5))
		commands.extend([ '-crf', str(output_video_compression) ])
	if faceswap.globals.output_video_encoder in [ 'h264_nvenc', 'hevc_nvenc' ]:
		output_video_compression = round(51 - (faceswap.globals.output_video_quality * 0.5))
		commands.extend([ '-cq', str(output_video_compression) ])
	commands.extend([ '-pix_fmt', 'yuv420p', '-y', temp_output_video_path ])
	return run_ffmpeg(commands)


def restore_audio(target_path : str, output_path : str) -> bool:
	fps = detect_fps(target_path)
	trim_frame_start = faceswap.globals.trim_frame_start
	trim_frame_end = faceswap.globals.trim_frame_end
	temp_output_video_path = get_temp_output_video_path(target_path)
	temp_output_audio_path = get_temp_output_audio_path(target_path)
	extract_commands = [ '-hwaccel', 'auto', '-i', target_path ]
	if trim_frame_start is not None:
		start_time = trim_frame_start / fps
		extract_commands.extend([ '-ss', str(start_time) ])
	if trim_frame_end is not None:
		end_time = trim_frame_end / fps
		extract_commands.extend([ '-to', str(end_time) ])
	extract_commands.extend([ '-vn', '-y', temp_output_audio_path ])
	merge_commands = [ '-hwaccel', 'auto', '-i', temp_output_video_path, '-i', temp_output_audio_path, '-y', output_path ]
	return run_ffmpeg(extract_commands) and run_ffmpeg(merge_commands)


def get_temp_frame_paths(target_path : str) -> List[str]:
	temp_directory_path = get_temp_directory_path(target_path)
	return glob.glob((os.path.join(glob.escape(temp_directory_path), '*.' + faceswap.globals.temp_frame_format)))


def get_temp_frames_pattern(target_path : str) -> str:
	temp_directory_path = get_temp_directory_path(target_path)
	return os.path.join(temp_directory_path, '%04d.' + faceswap.globals.temp_frame_format)


def get_temp_directory_path(target_path : str) -> str:
	target_name, _ = os.path.splitext(os.path.basename(target_path))
	return os.path.join(TEMP_DIRECTORY_PATH, target_name)


def get_temp_output_video_path(target_path : str) -> str:
	temp_directory_path = get_temp_directory_path(target_path)
	return os.path.join(temp_directory_path, TEMP_OUTPUT_VIDEO_NAME)


def get_temp_output_audio_path(target_path : str) -> str:
	temp_directory_path = get_temp_directory_path(target_path)
	return os.path.join(temp_directory_path, TEMP_OUTPUT_AUDIO_NAME)


def normalize_output_path(source_path : Optional[str], target_path : Optional[str], output_path : Optional[str]) -> Optional[str]:
	if is_file(source_path) and is_file(target_path) and is_directory(output_path):
		source_name, _ = os.path.splitext(os.path.basename(source_path))
		target_name, target_extension = os.path.splitext(os.path.basename(target_path))
		return os.path.join(output_path, source_name + '-' + target_name + target_extension)
	if is_file(target_path) and output_path:
		target_name, target_extension = os.path.splitext(os.path.basename(target_path))
		output_name, output_extension = os.path.splitext(os.path.basename(output_path))
		output_directory_path = os.path.dirname(output_path)
		if is_directory(output_directory_path) and output_extension:
			return os.path.join(output_directory_path, output_name + target_extension)
		return None
	return output_path


def create_temp(target_path : str) -> None:
	temp_directory_path = get_temp_directory_path(target_path)
	Path(temp_directory_path).mkdir(parents = True, exist_ok = True)


def move_temp(target_path : str, output_path : str) -> None:
	temp_output_video_path = get_temp_output_video_path(target_path)
	if is_file(temp_output_video_path):
		if is_file(output_path):
			os.remove(output_path)
		shutil.move(temp_output_video_path, output_path)


def clear_temp(target_path : str) -> None:
	temp_directory_path = get_temp_directory_path(target_path)
	parent_directory_path = os.path.dirname(temp_directory_path)
	if not faceswap.globals.keep_temp and is_directory(temp_directory_path):
		shutil.rmtree(temp_directory_path)
	if os.path.exists(parent_directory_path) and not os.listdir(parent_directory_path):
		os.rmdir(parent_directory_path)


def is_file(file_path : str) -> bool:
	return bool(file_path and os.path.isfile(file_path))


def is_directory(directory_path : str) -> bool:
	return bool(directory_path and os.path.isdir(directory_path))


def is_image(image_path : str) -> bool:
	if is_file(image_path):
		mimetype, _ = mimetypes.guess_type(image_path)
		return bool(mimetype and mimetype.startswith('image/'))
	return False


def is_video(video_path : str) -> bool:
	if is_file(video_path):
		mimetype, _ = mimetypes.guess_type(video_path)
		return bool(mimetype and mimetype.startswith('video/'))
	return False


def conditional_download(download_directory_path : str, urls : List[str]) -> None:
	if not os.path.exists(download_directory_path):
		os.makedirs(download_directory_path)
	for url in urls:
		download_file_path = os.path.join(download_directory_path, os.path.basename(url))
		if not os.path.exists(download_file_path):
			request = urllib.request.urlopen(url) # type: ignore[attr-defined]
			total = int(request.headers.get('Content-Length', 0))
			with tqdm(total = total, desc = wording.get('downloading'), unit = 'B', unit_scale = True, unit_divisor = 1024) as progress:
				urllib.request.urlretrieve(url, download_file_path, reporthook = lambda count, block_size, total_size: progress.update(block_size)) # type: ignore[attr-defined]


def resolve_relative_path(path : str) -> str:
	return os.path.abspath(os.path.join(os.path.dirname(__file__), path))


def list_module_names(path : str) -> Optional[List[str]]:
	if os.path.exists(path):
		files = os.listdir(path)
		return [ Path(file).stem for file in files if not Path(file).stem.startswith('__') ]
	return None


def encode_execution_providers(execution_providers : List[str]) -> List[str]:
	return [ execution_provider.replace('ExecutionProvider', '').lower() for execution_provider in execution_providers ]


def decode_execution_providers(execution_providers: List[str]) -> List[str]:
	available_execution_providers = onnxruntime.get_available_providers()
	encoded_execution_providers = encode_execution_providers(available_execution_providers)
	return [ execution_provider for execution_provider, encoded_execution_provider in zip(available_execution_providers, encoded_execution_providers) if any(execution_provider in encoded_execution_provider for execution_provider in execution_providers) ]


def get_device(execution_providers : List[str]) -> str:
	if 'CUDAExecutionProvider' in execution_providers:
		return 'cuda'
	if 'CoreMLExecutionProvider' in execution_providers:
		return 'mps'
	return 'cpu'
