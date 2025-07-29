import logging
from typing import Optional

from langchain.chat_models import init_chat_model
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

from src.domain.interfaces import LLMService


logger = logging.getLogger(__name__)


class LangChainLLMService(LLMService):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-5-sonnet-latest"):
        self.model_name = model_name
        self.llm = init_chat_model(model_name, model_provider="anthropic", api_key=api_key)
        
        # Initial summary prompt
        self.summarize_prompt = ChatPromptTemplate([
            ("human", "Write a concise summary of the following markdown content: {context}")
        ])
        self.initial_summary_chain = self.summarize_prompt | self.llm | StrOutputParser()
        
        # Refining summary prompt
        self.refine_template = """
Produce a final summary in markdown format.

Existing summary up to this point:
{existing_answer}

New markdown content:
------------
{context}
------------

Given the new content, refine the original summary. The output should be well-formatted markdown.
"""
        self.refine_prompt = ChatPromptTemplate([("human", self.refine_template)])
        self.refine_summary_chain = self.refine_prompt | self.llm | StrOutputParser()
        
        logger.info(f"Initialized LangChain LLM service with model: {model_name}")
    
    async def generate_initial_summary(self, content: str) -> str:
        logger.debug("Generating initial summary")
        try:
            summary = await self.initial_summary_chain.ainvoke({"context": content})
            logger.debug(f"Generated initial summary: {len(summary)} characters")
            return summary
        except Exception as e:
            logger.error(f"Error generating initial summary: {str(e)}")
            raise
    
    async def refine_summary(self, existing_summary: str, new_content: str) -> str:
        logger.debug("Refining existing summary with new content")
        try:
            refined_summary = await self.refine_summary_chain.ainvoke({
                "existing_answer": existing_summary,
                "context": new_content
            })
            logger.debug(f"Refined summary: {len(refined_summary)} characters")
            return refined_summary
        except Exception as e:
            logger.error(f"Error refining summary: {str(e)}")
            raise