import logging
import torch


class TorchUtils:

	@staticmethod
	def get_device() -> torch.device:
		if torch.cuda.is_available():
			logging.debug(f"Using CUDA device: {torch.cuda.get_device_name(torch.device('cuda'))}")
			return torch.device('cuda')
		elif torch.backends.mps.is_available():
			logging.debug("Using MPS device")
			return torch.device('mps')
		else:
			logging.warning("Using CPU")
			return torch.device('cpu')
