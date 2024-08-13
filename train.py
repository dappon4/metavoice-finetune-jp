import torch
from torch.utils.data import DataLoader
from torch.optim import Adam
from fam.llm.model import GPT, GPTConfig

SPEAKER_EMBEDDING_DIM = 256

model_config = GPTConfig()

model = GPT(model_config, SPEAKER_EMBEDDING_DIM)



