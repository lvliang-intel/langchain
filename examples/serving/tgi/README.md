# Using Text Generation Inference as Serving framework on Habana Gaudi

To use [🤗 text-generation-inference](https://github.com/huggingface/text-generation-inference) on Habana Gaudi/Gaudi2, please follow these steps:

## Build the Docker image located in the tgi-gaudi repo:
```bash
git clone https://github.com/huggingface/tgi-gaudi.git
cd tgi-gaudi/
docker build -t tgi_gaudi .
```

If you need to set proxy settings, add `--build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy` like below.
```bash
docker build -t tgi_gaudi . --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy
```

## Launch a local server instance on 1 Gaudi card:
```bash
model=Intel/neural-chat-7b-v3-3
volume=$PWD/data # share a volume with the Docker container to avoid downloading weights every run

docker run -p 8080:80 -v $volume:/data --runtime=habana -e HABANA_VISIBLE_DEVICES=all -e OMPI_MCA_btl_vader_single_copy_mechanism=none --cap-add=sys_nice --ipc=host tgi_gaudi --model-id $model
```

If you need to set proxy settings, add `--build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy` like below.
```bash
docker run -p 8080:80 -v $volume:/data --runtime=habana -e HABANA_VISIBLE_DEVICES=all -e OMPI_MCA_btl_vader_single_copy_mechanism=none --cap-add=sys_nice --ipc=host -e HTTPS_PROXY=$https_proxy -e HTTP_PROXY=$https_proxy tgi_gaudi --model-id $model
```

For gated models such as `LLAMA-2`, you will have to pass -e HUGGING_FACE_HUB_TOKEN=\<token\> to the docker run command above with a valid Hugging Face Hub read token.

Please follow this link [huggingface token](https://huggingface.co/docs/hub/security-tokens) to get the access tokens.


## Launch a local server instance on 8 Gaudi cards:

```bash
model=Intel/neural-chat-7b-v3-3
volume=$PWD/data # share a volume with the Docker container to avoid downloading weights every run

docker run -p 8080:80 -v $volume:/data --runtime=habana -e PT_HPU_ENABLE_LAZY_COLLECTIVES=true -e HABANA_VISIBLE_DEVICES=all -e OMPI_MCA_btl_vader_single_copy_mechanism=none --cap-add=sys_nice --ipc=host tgi_gaudi --model-id $model --sharded true --num-shard 8
```

Send a request to check if the endpoint is wokring:

```bash
curl localhost:8080/generate -X POST -d '{"inputs":"Which NFL team won the Super Bowl in the 2010 season?","parameters":{"max_new_tokens":128, "do_sample": true}}'   -H 'Content-Type: application/json'
```
The first call will be slower as the model is compiled.

More details please refer to [tgi-gaudi](https://github.com/huggingface/tgi-gaudi/blob/v1.2-release/README.md).

For more information and documentation about Text Generation Inference, checkout the [README](https://github.com/huggingface/text-generation-inference#text-generation-inference) of the original repo.

## Setup Conda

First, you need to install and configure the Conda environment:

```shell
# Download and install Miniconda
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda*.sh
source ~/.bashrc
conda create -n langchain python=3.9.0
conda activate langchain
```

## Install Intel langchain extension

We provide a comprehensive suite of Langchain-based extension APIs, including advanced retrievers, embedding models, and vector stores. These enhancements are carefully crafted to expand the capabilities of the original Langchain API, ultimately boosting overall performance. To get the better performance, install the extension using the below commands:
```bash
git clone https://github.com/lvliang-intel/intel_genai_kit_langchain.git
cd intel_genai_kit_langchain/libs/langchain/
pip install -e .
cd ../core/
pip install -e .
cd ../community/
pip install -e .
```

## Install Other Dependencies

To install the additional dependencies required for this example, use the following command:
```bash
pip install -r requirements.txt
```

## Configure Parameters
Before launching and consuming tgi-rag service, you need to configure parameters in `config.py` first.

|Parameter|Type|Default Value|Help|
|:--------| :---------:|:--------:|:--------|
|REDIS_HOST|str|"localhost"|The Redis host IP|
|REDIS_PORT|int|6379|The Redis Port|
|GRADIO_ENTRYPOINT|str|"http://localhost:8080"|The entrypoint of TGI|
|GRADIO_HOST|str|"0.0.0.0"|The Gradio host IP|
|GRADIO_PORT|int|80|The Gradio port|

## Access Service

To interact with the TGI endpoint and perform the inference, use the following commands:

```bash
cd ../examples/serving/tgi/
export HUGGINGFACEHUB_API_TOKEN=<token>
python client.py
```

Ensure that the Hugging Face Hub API token is properly set for authentication.

## Create Embedding Database

To generate the embedding database, use the following command. We support two different vector db: Chroma and Redis. Choose one for the parameter, Chroma will be chosen defaultly.
```bash
python vectordb.py --db Redis
```

This command creates the embedding database for a PDF file 'Intel_AR_WR.pdf'. The Gradio application utilizes this pre-built embedding database to build langchain application. Ensure that the embedding database is generated before starting the Gradio frontend application.

## Start the frontend

To initiate the frontend, follow these steps. Same as vectordb.py, you need to choose a vector db and pass into the python file. Chroma will be chosen defaultly.
```bash
export HUGGINGFACEHUB_API_TOKEN=<token>
python gradio_app.py --db Redis
```

This command starts the Gradio application, providing a URL for interacting with the chat UI.

## Chat in the UI

Open the URL generated after launching the Gradio application, and you can start interacting with the chat UI now.

![Frontend UI](https://i.imgur.com/yEiFXsR.png)