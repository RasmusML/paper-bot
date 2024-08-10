import numpy as np
import torch
from adapters import AutoAdapterModel
from transformers import AutoTokenizer


class Specter2:
    """Model to compute joint representation for a papers title and abstract."""

    def __init__(self):
        self.tokenizer = AutoTokenizer.from_pretrained("allenai/specter2_base")
        self.model = AutoAdapterModel.from_pretrained("allenai/specter2_base")
        self.model.load_adapter("allenai/specter2", source="hf", load_as="specter2", set_active=True)

    def get_embeddings(self, papers: list[dict[str, str]], batch_size=8, max_length=512) -> np.ndarray:
        """Get embedding for a papers title and abstract for each paper in the list."""
        text_batch = [paper["title"] + self.tokenizer.sep_token + (paper.get("abstract") or "") for paper in papers]

        embeddings = []

        for i in range(0, len(text_batch), batch_size):
            end = min(i + batch_size, len(text_batch))
            inputs = self.tokenizer(
                text_batch[i:end],
                padding=True,
                truncation=True,
                return_tensors="pt",
                return_token_type_ids=False,
                max_length=max_length,
            )
            output = self.model(**inputs)

            embedding = output.last_hidden_state.mean(dim=1)
            embeddings.append(embedding)

        return torch.cat(embeddings, dim=0).detach().numpy()
