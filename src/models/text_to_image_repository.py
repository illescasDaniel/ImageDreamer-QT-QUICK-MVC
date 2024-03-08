from pathlib import Path
from typing import Callable, Optional
from diffusers.pipelines.stable_diffusion_xl.pipeline_stable_diffusion_xl import StableDiffusionXLPipeline
from diffusers.pipelines.stable_diffusion_xl.pipeline_output import StableDiffusionXLPipelineOutput
from diffusers.schedulers.scheduling_euler_ancestral_discrete import EulerAncestralDiscreteScheduler
import torch
import PIL.Image
import uuid
from models.utils.app_utils import AppUtils
from models.utils.torch_utils import TorchUtils


class TextToImageRepository:
	__generator: Optional[torch.Generator] = None
	__pipeline: Optional[StableDiffusionXLPipeline] = None
	manual_seed: Optional[int] = None
	__TOTAL_STEPS: int = 8

	def initialize(self):
		# free vram
		self.cleanup()
		# pipeline
		model_path = AppUtils.app_base_path().parent / 'resources' / 'models' / 'dreamshaperXL_sfwV2TurboDPMSDE.safetensors'
		pipeline: StableDiffusionXLPipeline = StableDiffusionXLPipeline.from_single_file(
			pretrained_model_link_or_path=str(model_path),
			torch_dtype=torch.float16
		).to(TorchUtils.get_device()) # type: ignore
		# optimizations
		pipeline.enable_xformers_memory_efficient_attention()
		pipeline.enable_sequential_cpu_offload()
		pipeline.enable_vae_slicing()
		# sampler
		pipeline.scheduler = EulerAncestralDiscreteScheduler.from_config(pipeline.scheduler.config)
		# seed generator
		self.__generator = torch.Generator()
		# assign pipeline
		self.__pipeline = pipeline

	def generateImage(self, prompt: str, progress_callback: Callable[[float], None]) -> Path:
		# check attributes
		if self.__pipeline is None or self.__generator is None:
			raise AttributeError('Pipeline not initialized')
		# set seed
		seed = self.manual_seed if self.manual_seed is int else torch.seed()
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
			callback_on_step_end=callback_dynamic_cfg, # type: ignore
		) # type: ignore
		# save image
		image: PIL.Image.Image = output.images[0]
		image_path = AppUtils.app_base_path().parent / 'output' / f'{uuid.uuid4()}.png'
		image.save(image_path)
		# free resources
		self.cleanup()
		# return image path
		return image_path

	def cleanup(self):
		torch.cuda.empty_cache()
