import habana_frameworks.torch.core as htcore
import habana_frameworks.torch.gpu_migration

from langchain_community.llms import VLLM
llm = VLLM(
    # change the model path here to your own model name or path
    model="/data/models--meta-llama--Llama-2-7b-hf/snapshots/8cca527612d856d7d32bd94f8103728d614eb852/",
    dtype="bfloat16",
    vllm_kwargs={"swap_space": 16, "enforce_eager": True}
)
print(llm("What is the capital of France?", temperature=0, max_tokens=20))