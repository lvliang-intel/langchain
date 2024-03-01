from langchain_community.llms import HuggingFaceEndpoint
from langchain import LLMChain
from langchain import PromptTemplate
from config import GRADIO_ENTRYPOINT

multi_template = """Answer the following questions one at a time.

Questions:
{questions}

Answers:
"""
long_prompt = PromptTemplate(template=multi_template, input_variables=["questions"])


llm = HuggingFaceEndpoint(
    endpoint_url=GRADIO_ENTRYPOINT,
    max_new_tokens=512,
    top_k=10,
    top_p=0.95,
    typical_p=0.95,
    temperature=0.01,
    repetition_penalty=1.03,
)


llm_chain = LLMChain(
    prompt=long_prompt,
    llm=llm
)

qs_str = (
    "Which NFL team won the Super Bowl in the 2010 season?\n" +
    "If I am 6 ft 4 inches, how tall am I in centimeters?\n" +
    "Who was the 12th person on the moon?" +
    "How many eyes does a blade of grass have?"
)

print(llm_chain.invoke(qs_str))

