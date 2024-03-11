import os
from pathlib import Path
import time
from typing import Any, Callable, List, Optional
import uuid
import re
import unicodedata
import logging
import subprocess

from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from diffusers.pipelines.stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from diffusers.schedulers.scheduling_euler_ancestral_discrete import EulerAncestralDiscreteScheduler
from transformers import pipeline
from transformers import ImageClassificationPipeline
import torch
import numpy as np
from PIL.Image import Image
from PIL.Image import fromarray as Image_fromarray

from models.utils.app_utils import AppUtils
from models.utils.torch_utils import TorchUtils


class TextToImageRepository:
	manual_seed: Optional[int] = None
	__generator: Optional[torch.Generator] = None
	__sd_pipeline: Optional[StableDiffusionXLPipeline] = None
	__device: Optional[torch.device] = None
	__unsafe_image_detector: Optional[ImageClassificationPipeline] = None
	__UNSAFE_IMAGE_DETECTOR_ENABLED: bool = True
	__TOTAL_STEPS: int = 8
	__PROMPT_MAX_TOKENS: int = 75
	__USE_EXTREME_MEMORY_OPTIMIZATIONS: bool = True

	def initialize(self):
		# free-up resources
		self.cleanup()
		# get pipeline
		device = TorchUtils.get_device()
		# alternative for generic model: AutoPipelineForText2Image.from_pretrained(pretrained_model_or_path='lykon/dreamshaper-xl-v2-turbo',...)
		sd_pipeline: StableDiffusionXLPipeline = StableDiffusionXLPipeline.from_single_file(
			pretrained_model_link_or_path='https://huggingface.co/Lykon/dreamshaper-xl-v2-turbo/blob/main/DreamShaperXL_Turbo_V2-SFW.safetensors',
			torch_dtype=torch.float16,
			variant="fp16",
			add_watermarker=True
		) # type: ignore
		# disable cli progress bar on distributed executables
		sd_pipeline.set_progress_bar_config(disable=AppUtils.is_app_frozen())
		# enable optimizations
		if TextToImageRepository.__USE_EXTREME_MEMORY_OPTIMIZATIONS:
			sd_pipeline = sd_pipeline.to(device)
			sd_pipeline.enable_vae_slicing()
			sd_pipeline.enable_xformers_memory_efficient_attention()
			sd_pipeline.enable_sequential_cpu_offload(device=device)
		else:
			sd_pipeline.enable_model_cpu_offload(device=device)
		# assign Euler sampler
		sd_pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(sd_pipeline.scheduler.config)
		# seed generator
		self.__generator = torch.Generator(device=device)
		# get unsafe image detector
		if TextToImageRepository.__UNSAFE_IMAGE_DETECTOR_ENABLED:
			self.__unsafe_image_detector = pipeline(
				task="image-classification",
				model="Falconsai/nsfw_image_detection",
				device=device
			) #type: ignore
		# assign local variables
		self.__sd_pipeline = sd_pipeline
		self.__device = device

	def generateImage(self, prompt: str, progress_callback: Callable[[float, Optional[Path]], None]) -> Path:
		# free-up resources
		self.cleanup()
		# check attributes
		if self.__sd_pipeline is None or self.__generator is None or self.__device is None:
			raise AttributeError('Pipeline or device not initialized')
		# check prompt size
		if len(prompt.split(' ')) > TextToImageRepository.__PROMPT_MAX_TOKENS:
			raise ValueError("Prompt too long: exceeds 75 words.")
		# set seed
		seed = self.manual_seed or torch.seed()
		self.__generator.manual_seed(seed)
		# start progress at 0%
		progress_callback(0, None)
		# get_clean_file_name
		output_file_name = self.__output_file_name(prompt)
		# list of temporary images
		temp_images_paths: list[Path] = []
		# generate image
		def callback_dynamic_cfg(pipe, step_index, timestep, callback_kwargs):
			# TODO: add a way to stop the pipeline when user exists? to stop: pipeline._interrupt = True
			# calculate progress and send it
			progress: float = float(step_index+1) / float(TextToImageRepository.__TOTAL_STEPS)
			# log gpu usage
			if step_index == TextToImageRepository.__TOTAL_STEPS-1:
				logging.info(f"GPU usage: {self.__get_nvidia_vram_usage()} MiB")
			# get temporary images
			try:
				latents: torch.Tensor = callback_kwargs["latents"]
				image = self.__latents_to_rgb(latents)
				image_path = AppUtils.app_base_path().parent / 'output' / f'{output_file_name}_step_{step_index}.png'
				temp_images_paths.append(image_path)
				image.save(image_path)
				progress_callback(progress, image_path)
			except Exception as e:
				logging.warning(e)
				progress_callback(progress, None)
			return callback_kwargs
		output: StableDiffusionXLPipelineOutput = self.__sd_pipeline(
			prompt,
			num_inference_steps=TextToImageRepository.__TOTAL_STEPS,
			guidance_scale=2,
			generator=self.__generator,
			width=1024,
			height=1024,
			original_size=(1024,1024),
			callback_on_step_end=callback_dynamic_cfg, # type: ignore
			callback_on_step_end_tensor_inputs=["latents"]
		) # type: ignore
		# get image
		image: Image = output.images[0]
		# remove temporary images
		for img_path in temp_images_paths:
			try:
				os.remove(img_path)
			except Exception:
				pass
		# check unsafe content
		if self.__is_image_unsafe(image):
			progress_callback(1, None)
			self.cleanup()
			raise Exception('Unsafe content detected')
		# save image
		image_path: Path
		try:
			image_path = AppUtils.app_base_path().parent / 'output' / f'{output_file_name}.png'
			image.save(image_path)
		except:
			image_path = AppUtils.app_base_path().parent / 'output' / f'{uuid.uuid4()}.png'
			image.save(image_path)
		# free resources
		self.cleanup()
		# return image path
		return image_path

	def cleanup(self):
		torch.cuda.empty_cache()

	def __output_file_name(self, prompt: str) -> str:
		try:
			file_name = re.sub(r'\s|[^\w\-\.]', '_', unicodedata.normalize('NFD', prompt).encode('ascii', 'ignore').decode('ascii')).strip(".").lstrip("_.")[:60]
			file_name_and_timestamp = f'{file_name}-{int(time.time())}'
			return file_name_and_timestamp
		except Exception:
			uuid_file_name = str(uuid.uuid4())
			return uuid_file_name

	def __is_image_unsafe(
		self,
		image: Image
	) -> bool:
		if TextToImageRepository.__UNSAFE_IMAGE_DETECTOR_ENABLED and self.__unsafe_image_detector is not None:
			image_detector_output: List[dict[str, Any]] = self.__unsafe_image_detector(image) # type: ignore
			unsafe_values: dict[str, Any] | None = next((v for v in image_detector_output if v.get('label') == 'nsfw'), None)
			if unsafe_values is None:
				return False
			unsafe_score: float = unsafe_values['score']
			logging.info(f'unsafe score: {unsafe_score}')
			return unsafe_score > 0.6
		else:
			return False

	def __get_nvidia_vram_usage(self) -> str:
		if not torch.cuda.is_available():
			return ''
		try:
			result = subprocess.run(['nvidia-smi', '--query-gpu=memory.used', '--format=csv,noheader,nounits'], stdout=subprocess.PIPE, text=True, check=True)
			used_memory_list = [x for x in result.stdout.strip().split('\n')]
			return '\n'.join(used_memory_list)
		except:
			return ''

	# https://huggingface.co/docs/diffusers/main/en/using-diffusers/callback#display-image-after-each-generation-step
	def __latents_to_rgb(self, latents: torch.Tensor):
		weights = (
			(60, -60, 25, -70),
			(60,  -5, 15, -50),
			(60,  10, -5, -35)
		)
		weights_tensor = torch.t(torch.tensor(weights, dtype=latents.dtype).to(latents.device))
		biases_tensor = torch.tensor((150, 140, 130), dtype=latents.dtype).to(latents.device)
		rgb_tensor = torch.einsum("...lxy,lr -> ...rxy", latents, weights_tensor) + biases_tensor.unsqueeze(-1).unsqueeze(-1)
		image_array: np.ndarray = rgb_tensor.clamp(0, 255)[0].byte().cpu().numpy()
		image_array = image_array.transpose(1, 2, 0)
		return Image_fromarray(image_array)
