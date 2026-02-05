"""GLM-4.7 model integration for Just Code using LangChain 1.0.

This module provides integration with Zhipu AI's GLM-4.7 series models
using the ChatOpenAI interface, which is compatible with Zhipu AI's API.

Zhipu AI Base URL: https://open.bigmodel.cn/api/paas/v4/
"""

from langchain_openai import ChatOpenAI
from langchain_core.language_models.chat_models import BaseChatModel

from just_code.utils import get_logger, load_config

logger = get_logger(__name__)

# Available GLM models (updated 2026)
GLM_MODELS = {
    # GLM-4.7 Series (Latest - Optimized for Agentic Coding)
    "glm-4.7": "GLM-4.7 - Latest flagship model for coding & agents",
    "glm-4.7-flashx": "GLM-4.7 FlashX - Fast & lightweight for quick tasks",
    # GLM-4 Series (Previous generation)
    "glm-4-plus": "GLM-4 Plus - Most capable model for complex tasks",
    "glm-4-0520": "GLM-4 0520 - Balanced performance and cost",
    "glm-4-air": "GLM-4 Air - Faster responses for simpler tasks",
    "glm-4-flash": "GLM-4 Flash - Fastest, ideal for quick interactions",
}

# Zhipu AI API endpoint
ZHIPUAI_BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"


def get_llm(
    model: str | None = None,
    temperature: float | None = None,
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs,
) -> BaseChatModel:
    """Get a configured GLM-4.7 chat model instance using ChatOpenAI.

    Zhipu AI is compatible with OpenAI's API format, so we can use
    ChatOpenAI with just a different base_url and api_key.

    Args:
        model: Model name to use (e.g., "glm-4.7", "glm-4.7-flashx").
               Defaults to AGENT_MODEL env var or "glm-4.7".
        temperature: Sampling temperature (0-2). Higher = more creative.
        api_key: Zhipu AI API key. Defaults to ZHIPUAI_API_KEY env var.
        base_url: Custom base URL. Defaults to Zhipu AI's endpoint.
        **kwargs: Additional arguments passed to ChatOpenAI.

    Returns:
        Configured ChatOpenAI instance for GLM.

    Raises:
        ValueError: If API key is not configured.
    """
    config = load_config()

    # Get model name
    model_name = model or config.get("model", "glm-4.7")
    if model_name not in GLM_MODELS:
        logger.warning(f"Unknown model '{model_name}'. Using 'glm-4.7' instead.")
        model_name = "glm-4.7"

    # Get API key
    llm_api_key = api_key or config.get("api_key")
    if not llm_api_key:
        raise ValueError(
            "ZHIPUAI_API_KEY not configured. Please set it in your .env file "
            "or pass it via the api_key parameter."
        )

    # Get temperature
    llm_temperature = temperature if temperature is not None else config.get("temperature", 0.7)

    # Get base URL
    llm_base_url = base_url or config.get("base_url", ZHIPUAI_BASE_URL)

    # Create model instance using ChatOpenAI (compatible with Zhipu AI)
    logger.info(f"Initializing GLM model: {model_name}")

    llm = ChatOpenAI(
        api_key=llm_api_key,
        base_url=llm_base_url,
        model=model_name,
        temperature=llm_temperature,
        **kwargs,
    )

    return llm


def list_models() -> dict[str, str]:
    """List available GLM-4.7 models.

    Returns:
        Dictionary mapping model names to descriptions.
    """
    return GLM_MODELS.copy()
