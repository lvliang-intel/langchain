# Using vLLM as Serving framework on Habana Gaudi2 (Experimental)

> [!NOTE]
> This feature is *provisional* and likely to change in future versions.

To use [vLLM](https://github.com/vllm-project/vllm) on Habana Gaudi/Gaudi2, please follow these steps:


## Build the Docker image

```
docker build -t vllm_gaudi .
```

If you need to set proxy settings, add `--build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy` like below.
```bash
docker build -t vllm_gaudi . --build-arg https_proxy=$https_proxy --build-arg http_proxy=$http_proxy
```


## Run the Docker image



```
export volume=<path to your models>

docker run -it -p 8088:8080 -v $volume:/data --runtime=habana -e HABANA_VISIBLE_DEVICES=all -e OMPI_MCA_btl_vader_single_copy_mechanism=none --cap-add=sys_nice --ipc=host -e HTTPS_PROXY=$https_proxy -e HTTP_PROXY=$http_proxy -e PYTHONPATH=/vllm-fork vllm_gaudi
```

Inside the docker container, check and run the `client.py` based on langchain community's vLLM endpoint:

```
python client.py
```