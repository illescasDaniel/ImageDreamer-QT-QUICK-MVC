from pathlib import Path
import time
from typing import Callable, Optional
import uuid
import re
import unicodedata

from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from diffusers.pipelines.stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from diffusers.schedulers.scheduling_euler_ancestral_discrete import EulerAncestralDiscreteScheduler
from diffusers.pipelines.auto_pipeline import AutoPipelineForText2Image
import torch
import PIL.Image

from models.utils.app_utils import AppUtils
from models.utils.torch_utils import TorchUtils


class TextToImageRepository:
	__generator: Optional[torch.Generator] = None
	__pipeline: Optional[StableDiffusionXLPipeline] = None
	manual_seed: Optional[int] = None
	__TOTAL_STEPS: int = 8

	def initialize(self):
		# free-up resources
		self.cleanup()
		# get pipeline
		device = TorchUtils.get_device()
		pipeline: StableDiffusionXLPipeline = AutoPipelineForText2Image.from_pretrained(
			pretrained_model_or_path='lykon/dreamshaper-xl-v2-turbo',
			torch_dtype=torch.float16,
			variant="fp16",
			add_watermarker=False
		).to(device) # type: ignore
		# disable cli progress bar on distributed executables
		pipeline.set_progress_bar_config(disable=AppUtils.is_app_frozen())
		# enable optimizations
		pipeline.enable_xformers_memory_efficient_attention()
		pipeline.enable_sequential_cpu_offload(device=device)
		pipeline.enable_vae_slicing()
		# assign Euler sampler
		pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
		# seed generator
		self.__generator = torch.Generator(device=device)
		# assign pipeline
		self.__pipeline = pipeline

	def generateImage(self, prompt: str, progress_callback: Callable[[float], None]) -> Path:
		# check attributes
		if self.__pipeline is None or self.__generator is None:
			raise AttributeError('Pipeline not initialized')
		# set seed
		seed = self.manual_seed or torch.seed()
		self.__generator.manual_seed(seed)
		# generate image
		def callback_dynamic_cfg(pipe, step_index, timestep, callback_kwargs):
			progress: float = float(step_index+1) / float(TextToImageRepository.__TOTAL_STEPS)
			progress_callback(progress)
			return callback_kwargs
		output: StableDiffusionXLPipelineOutput = self.__pipeline(
			prompt,
			num_inference_steps=TextToImageRepository.__TOTAL_STEPS,
			guidance_scale=2,
			generator=self.__generator,
			width=1024,
			height=1024,
			original_size=(1024,1024),
			callback_on_step_end=callback_dynamic_cfg, # type: ignore
		) # type: ignore
		# save image
		image: PIL.Image.Image = output.images[0]
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
