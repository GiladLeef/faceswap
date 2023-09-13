from typing import Optional
import gradio

import faceswap.globals
from faceswap import wording
from faceswap.uis.typing import Update

KEEP_FPS_CHECKBOX : Optional[gradio.Checkbox] = None
KEEP_TEMP_CHECKBOX : Optional[gradio.Checkbox] = None
SKIP_AUDIO_CHECKBOX : Optional[gradio.Checkbox] = None


def render() -> None:
	global KEEP_FPS_CHECKBOX
	global KEEP_TEMP_CHECKBOX
	global SKIP_AUDIO_CHECKBOX

	KEEP_FPS_CHECKBOX = gradio.Checkbox(
		label = wording.get('keep_fps_checkbox_label'),
		value = faceswap.globals.keep_fps
	)
	KEEP_TEMP_CHECKBOX = gradio.Checkbox(
		label = wording.get('keep_temp_checkbox_label'),
		value = faceswap.globals.keep_temp
	)
	SKIP_AUDIO_CHECKBOX = gradio.Checkbox(
		label = wording.get('skip_audio_checkbox_label'),
		value = faceswap.globals.skip_audio
	)


def listen() -> None:
	KEEP_FPS_CHECKBOX.change(lambda value: update_checkbox('keep_fps', value), inputs = KEEP_FPS_CHECKBOX, outputs = KEEP_FPS_CHECKBOX)
	KEEP_TEMP_CHECKBOX.change(lambda value: update_checkbox('keep_temp', value), inputs = KEEP_TEMP_CHECKBOX, outputs = KEEP_TEMP_CHECKBOX)
	SKIP_AUDIO_CHECKBOX.change(lambda value: update_checkbox('skip_audio', value), inputs = SKIP_AUDIO_CHECKBOX, outputs = SKIP_AUDIO_CHECKBOX)


def update_checkbox(name : str, value: bool) -> Update:
	setattr(faceswap.globals, name, value)
	return gradio.update(value = value)
