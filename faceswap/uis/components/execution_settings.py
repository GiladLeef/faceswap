from typing import Optional
import gradio

import faceswap.globals
from faceswap import wording
from faceswap.uis.typing import Update

EXECUTION_THREAD_COUNT_SLIDER : Optional[gradio.Slider] = None
EXECUTION_QUEUE_COUNT_SLIDER : Optional[gradio.Slider] = None


def render() -> None:
	global EXECUTION_THREAD_COUNT_SLIDER
	global EXECUTION_QUEUE_COUNT_SLIDER

	EXECUTION_THREAD_COUNT_SLIDER = gradio.Slider(
		label = wording.get('execution_thread_count_slider_label'),
		value = faceswap.globals.execution_thread_count,
		step = 1,
		minimum = 1,
		maximum = 128
	)
	EXECUTION_QUEUE_COUNT_SLIDER = gradio.Slider(
		label = wording.get('execution_queue_count_slider_label'),
		value = faceswap.globals.execution_queue_count,
		step = 1,
		minimum = 1,
		maximum = 16
	)


def listen() -> None:
	EXECUTION_THREAD_COUNT_SLIDER.change(update_execution_thread_count, inputs = EXECUTION_THREAD_COUNT_SLIDER, outputs = EXECUTION_THREAD_COUNT_SLIDER)
	EXECUTION_QUEUE_COUNT_SLIDER.change(update_execution_queue_count, inputs = EXECUTION_QUEUE_COUNT_SLIDER, outputs = EXECUTION_QUEUE_COUNT_SLIDER)


def update_execution_thread_count(execution_thread_count : int = 1) -> Update:
	faceswap.globals.execution_thread_count = execution_thread_count
	return gradio.update(value = execution_thread_count)


def update_execution_queue_count(execution_queue_count : int = 1) -> Update:
	faceswap.globals.execution_queue_count = execution_queue_count
	return gradio.update(value = execution_queue_count)
