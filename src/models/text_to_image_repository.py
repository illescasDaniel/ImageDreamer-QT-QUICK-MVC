from pathlib import Path
import time
from typing import Any, Callable, List, Optional
import uuid
import re
import unicodedata
import logging

from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from diffusers.pipelines.stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from diffusers.schedulers.scheduling_euler_ancestral_discrete import EulerAncestralDiscreteScheduler
from transformers import pipeline
from transformers import ImageClassificationPipeline
import torch
from PIL.Image import Image

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
			add_watermarker=False
		).to(device) # type: ignore
		# disable cli progress bar on distributed executables
		sd_pipeline.set_progress_bar_config(disable=AppUtils.is_app_frozen())
		# enable optimizations
		sd_pipeline.enable_xformers_memory_efficient_attention()
		sd_pipeline.enable_sequential_cpu_offload(device=device)
		sd_pipeline.enable_vae_slicing()
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

	def generateImage(self, prompt: str, progress_callback: Callable[[float], None]) -> Path:
		# check attributes
		if self.__sd_pipeline is None or self.__generator is None or self.__device is None:
			raise AttributeError('Pipeline or device not initialized')
		# set seed
		seed = self.manual_seed or torch.seed()
		self.__generator.manual_seed(seed)
		# generate image
		def callback_dynamic_cfg(pipe, step_index, timestep, callback_kwargs):
			progress: float = float(step_index+1) / float(TextToImageRepository.__TOTAL_STEPS)
			progress_callback(progress)
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
		) # type: ignore
		# get image
		image: Image = output.images[0]
		# check unsafe content
		if (TextToImageRepository.__UNSAFE_IMAGE_DETECTOR_ENABLED
			and self.__unsafe_image_detector is not None
			and self.__is_unsafe_image(image, self.__unsafe_image_detector)):
			raise Exception('Unsafe content detected')
		# save image
		image_path: Path
		try:
			sanitized_file_name = self.__sanitize_filename(prompt)
			image_path = AppUtils.app_base_path().parent / 'output' / f'{sanitized_file_name}-{int(time.time())}.png'
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

	def __sanitize_filename(self, text: str) -> str:
		return re.sub(r'\s|[^\w\-\.]', '_', unicodedata.normalize('NFD', text).encode('ascii', 'ignore').decode('ascii')).strip(".").lstrip("_.")[:60]

	def __is_unsafe_image(
		self,
		image: Image,
		unsafe_image_detector: ImageClassificationPipeline
	) -> bool:
		image_detector_output: List[dict[str, Any]] = unsafe_image_detector(image) # type: ignore
		unsafe_values: dict[str, Any] | None = next((v for v in image_detector_output if v.get('label') == 'nsfw'), None)
		if unsafe_values is None:
			return False
		unsafe_score: float = unsafe_values['score']
		logging.info(f'unsafe score: {unsafe_score}')
		return unsafe_score > 0.8
