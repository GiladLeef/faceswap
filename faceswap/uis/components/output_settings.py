from typing import Optional, Tuple, List
import gradio

import faceswap.choices
import faceswap.globals
from faceswap import wording
from faceswap.typing import OutputVideoEncoder
from faceswap.uis import core as ui
from faceswap.uis.typing import Update, ComponentName
from faceswap.utilities import is_image, is_video

OUTPUT_IMAGE_QUALITY_SLIDER : Optional[gradio.Slider] = None
OUTPUT_VIDEO_ENCODER_DROPDOWN : Optional[gradio.Dropdown] = None
OUTPUT_VIDEO_QUALITY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global OUTPUT_IMAGE_QUALITY_SLIDER
	global OUTPUT_VIDEO_ENCODER_DROPDOWN
	global OUTPUT_VIDEO_QUALITY_SLIDER

	OUTPUT_IMAGE_QUALITY_SLIDER = gradio.Slider(
		label = wording.get('output_image_quality_slider_label'),
		value = faceswap.globals.output_image_quality,
		step = 1,
		visible = is_image(faceswap.globals.target_path)
	)
	OUTPUT_VIDEO_ENCODER_DROPDOWN = gradio.Dropdown(
		label = wording.get('output_video_encoder_dropdown_label'),
		choices = faceswap.choices.output_video_encoder,
		value = faceswap.globals.output_video_encoder,
		visible = is_video(faceswap.globals.target_path)
	)
	OUTPUT_VIDEO_QUALITY_SLIDER = gradio.Slider(
		label = wording.get('output_video_quality_slider_label'),
		value = faceswap.globals.output_video_quality,
		step = 1,
		visible = is_video(faceswap.globals.target_path)
	)


def listen() -> None:
	OUTPUT_IMAGE_QUALITY_SLIDER.change(update_output_image_quality, inputs = OUTPUT_IMAGE_QUALITY_SLIDER, outputs = OUTPUT_IMAGE_QUALITY_SLIDER)
	OUTPUT_VIDEO_ENCODER_DROPDOWN.select(update_output_video_encoder, inputs = OUTPUT_VIDEO_ENCODER_DROPDOWN, outputs = OUTPUT_VIDEO_ENCODER_DROPDOWN)
	OUTPUT_VIDEO_QUALITY_SLIDER.change(update_output_video_quality, inputs = OUTPUT_VIDEO_QUALITY_SLIDER, outputs = OUTPUT_VIDEO_QUALITY_SLIDER)
	multi_component_names : List[ComponentName] =\
	[
		'source_image',
		'target_image',
		'target_video'
	]
	for component_name in multi_component_names:
		component = ui.get_component(component_name)
		if component:
			for method in [ 'upload', 'change', 'clear' ]:
				getattr(component, method)(remote_update, outputs = [ OUTPUT_IMAGE_QUALITY_SLIDER, OUTPUT_VIDEO_ENCODER_DROPDOWN, OUTPUT_VIDEO_QUALITY_SLIDER ])


def remote_update() -> Tuple[Update, Update, Update]:
	if is_image(faceswap.globals.target_path):
		return gradio.update(visible = True), gradio.update(visible = False), gradio.update(visible = False)
	if is_video(faceswap.globals.target_path):
		return gradio.update(visible = False), gradio.update(visible = True), gradio.update(visible = True)
	return gradio.update(visible = False), gradio.update(visible = False), gradio.update(visible = False)


def update_output_image_quality(output_image_quality : int) -> Update:
	faceswap.globals.output_image_quality = output_image_quality
	return gradio.update(value = output_image_quality)


def update_output_video_encoder(output_video_encoder: OutputVideoEncoder) -> Update:
	faceswap.globals.output_video_encoder = output_video_encoder
	return gradio.update(value = output_video_encoder)


def update_output_video_quality(output_video_quality : int) -> Update:
	faceswap.globals.output_video_quality = output_video_quality
	return gradio.update(value = output_video_quality)
