from typing import Optional
import gradio

import faceswap.globals
from faceswap import wording
from faceswap.uis.typing import Update

MAX_MEMORY_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global MAX_MEMORY_SLIDER

	MAX_MEMORY_SLIDER = gradio.Slider(
		label = wording.get('max_memory_slider_label'),
		minimum = 0,
		maximum = 128,
		step = 1
	)


def listen() -> None:
	MAX_MEMORY_SLIDER.change(update_max_memory, inputs = MAX_MEMORY_SLIDER, outputs = MAX_MEMORY_SLIDER)


def update_max_memory(max_memory : int) -> Update:
	faceswap.globals.max_memory = max_memory if max_memory > 0 else None
	return gradio.update(value = max_memory)
