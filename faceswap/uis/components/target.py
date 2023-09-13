from typing import Any, IO, Tuple, Optional
import gradio

import faceswap.globals
from faceswap import wording
from faceswap.face_reference import clear_face_reference
from faceswap.uis import core as ui
from faceswap.uis.typing import Update
from faceswap.utilities import is_image, is_video

TARGET_FILE : Optional[gradio.File] = None
TARGET_IMAGE : Optional[gradio.Image] = None
TARGET_VIDEO : Optional[gradio.Video] = None


def render() -> None:
	global TARGET_FILE
	global TARGET_IMAGE
	global TARGET_VIDEO

	is_target_image = is_image(faceswap.globals.target_path)
	is_target_video = is_video(faceswap.globals.target_path)
	TARGET_FILE = gradio.File(
		label = wording.get('target_file_label'),
		file_count = 'single',
		file_types =
		[
			'.png',
			'.jpg',
			'.webp',
			'.mp4'
		],
		value = faceswap.globals.target_path if is_target_image or is_target_video else None
	)
	TARGET_IMAGE = gradio.Image(
		value = TARGET_FILE.value['name'] if is_target_image else None,
		visible = is_target_image,
		show_label = False
	)
	TARGET_VIDEO = gradio.Video(
		value = TARGET_FILE.value['name'] if is_target_video else None,
		visible = is_target_video,
		show_label = False
	)
	ui.register_component('target_image', TARGET_IMAGE)
	ui.register_component('target_video', TARGET_VIDEO)


def listen() -> None:
	TARGET_FILE.change(update, inputs = TARGET_FILE, outputs = [ TARGET_IMAGE, TARGET_VIDEO ])


def update(file : IO[Any]) -> Tuple[Update, Update]:
	clear_face_reference()
	if file and is_image(file.name):
		faceswap.globals.target_path = file.name
		return gradio.update(value = file.name, visible = True), gradio.update(value = None, visible = False)
	if file and is_video(file.name):
		faceswap.globals.target_path = file.name
		return gradio.update(value = None, visible = False), gradio.update(value = file.name, visible = True)
	faceswap.globals.target_path = None
	return gradio.update(value = None, visible = False), gradio.update(value = None, visible = False)
