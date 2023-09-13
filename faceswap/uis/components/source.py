from typing import Any, IO, Optional
import gradio

import faceswap.globals
from faceswap import wording
from faceswap.uis import core as ui
from faceswap.uis.typing import Update
from faceswap.utilities import is_image

SOURCE_FILE : Optional[gradio.File] = None
SOURCE_IMAGE : Optional[gradio.Image] = None


def render() -> None:
	global SOURCE_FILE
	global SOURCE_IMAGE

	is_source_image = is_image(faceswap.globals.source_path)
	SOURCE_FILE = gradio.File(
		file_count = 'single',
		file_types =
		[
			'.png',
			'.jpg',
			'.webp'
		],
		label = wording.get('source_file_label'),
		value = faceswap.globals.source_path if is_source_image else None
	)
	SOURCE_IMAGE = gradio.Image(
		value = SOURCE_FILE.value['name'] if is_source_image else None,
		visible = is_source_image,
		show_label = False
	)
	ui.register_component('source_image', SOURCE_IMAGE)


def listen() -> None:
	SOURCE_FILE.change(update, inputs = SOURCE_FILE, outputs = SOURCE_IMAGE)


def update(file: IO[Any]) -> Update:
	if file and is_image(file.name):
		faceswap.globals.source_path = file.name
		return gradio.update(value = file.name, visible = True)
	faceswap.globals.source_path = None
	return gradio.update(value = None, visible = False)
