import logging
from typing import Any, Dict, List, Mapping, Optional

import requests
from langchain_core.embeddings import Embeddings
from langchain_core.pydantic_v1 import BaseModel, Extra

logger = logging.getLogger(__name__)

import os
from datetime import datetime, timedelta
from oauthlib.oauth2 import BackendApplicationClient
from requests_oauthlib import OAuth2Session
import requests
# OAuth2 token
token = {
            "ollama2-server": {
                "envParams": {
                    "token": "AICORE_TOKENURL",
                    "id": "OPENAI_CLIENTID",
                    "sec": "OPENAI_CLIENTSECRET"
                },
                "token": {}
                }
        }
# -------------- Env. Variables --------------->>>
CLIENT_ID = os.environ.get("AICORE_OLLAMA_CLIENT_ID")
CLIENT_SECRET = os.environ.get("AICORE_OLLAMA_CLIENT_SECRET")
TOKEN_URL = os.environ.get("AICORE_OLLAMA_AUTH_URL")
API_URL = os.environ.get("AICORE_OLLAMA_API_BASE")
RESOURCE_GROUP = os.environ.get("AICORE_OLLAMA_RESOURCE_GROUP")
DEPLOYMENT_NAME = os.environ.get("DEPLOYMENT_NAME")
RETRY_TIME = int(os.environ.get("RETRY_TIME","30"))
DEPLOYMENT_API_PATH = "/lm/deployments" 

def get_token(service: str) -> str:
    global token
    client = BackendApplicationClient(client_id=CLIENT_ID)
    # create an OAuth2 session
    oauth = OAuth2Session(client=client)
    if token[service]['token'] == {}:
        token[service]['token'] = oauth.fetch_token(token_url=TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)    
    elif datetime.fromtimestamp(token[service]['token']['expires_at']) - datetime.now() < timedelta(seconds=60):
        token[service]['token'] = oauth.fetch_token(token_url=TOKEN_URL, client_id=CLIENT_ID, client_secret=CLIENT_SECRET)  
    return f"Bearer {token[service]['token']['access_token']}"

def get_baseurl()->str:
    """ Retrieves the AI Core deployment URL """
    # Request an access token using client credentials
    access_token = get_token(DEPLOYMENT_NAME)
    
    headers = {
        'Authorization': access_token,
        'AI-Resource-Group': RESOURCE_GROUP
    }
    res = requests.get(API_URL+DEPLOYMENT_API_PATH, headers=headers)
    j_data = res.json()
    for resource in j_data["resources"]:
        if resource["scenarioId"] == DEPLOYMENT_NAME:
            if resource["deploymentUrl"] == "":
                print(f"Scenario '{DEPLOYMENT_NAME}' was found but deployment URL was empty. Current status is '{resource['status']}', target status is '{resource['targetStatus']}'. Retry in {str(RETRY_TIME)} seconds.")
            else:
                print(f"Scenario '{DEPLOYMENT_NAME}': Plan '{resource['details']['resources']['backend_details']['predictor']['resource_plan']}', modfied at {resource['modifiedAt']}.")
            return f"{resource['deploymentUrl']}/v1"

class OllamaEmbeddings(BaseModel, Embeddings):
    """Ollama locally runs large language models.

    To use, follow the instructions at https://ollama.ai/.

    Example:
        .. code-block:: python

            from langchain_community.embeddings import OllamaEmbeddings
            ollama_emb = OllamaEmbeddings(
                model="llama:7b",
            )
            r1 = ollama_emb.embed_documents(
                [
                    "Alpha is the first letter of Greek alphabet",
                    "Beta is the second letter of Greek alphabet",
                ]
            )
            r2 = ollama_emb.embed_query(
                "What is the second letter of Greek alphabet"
            )

    """

    base_url: str = get_baseurl()
    """Base url the model is hosted under."""
    model: str = "llama2"
    """Model name to use."""

    embed_instruction: str = "passage: "
    """Instruction used to embed documents."""
    query_instruction: str = "query: "
    """Instruction used to embed the query."""

    mirostat: Optional[int] = None
    """Enable Mirostat sampling for controlling perplexity.
    (default: 0, 0 = disabled, 1 = Mirostat, 2 = Mirostat 2.0)"""

    mirostat_eta: Optional[float] = None
    """Influences how quickly the algorithm responds to feedback
    from the generated text. A lower learning rate will result in
    slower adjustments, while a higher learning rate will make
    the algorithm more responsive. (Default: 0.1)"""

    mirostat_tau: Optional[float] = None
    """Controls the balance between coherence and diversity
    of the output. A lower value will result in more focused and
    coherent text. (Default: 5.0)"""

    num_ctx: Optional[int] = None
    """Sets the size of the context window used to generate the
    next token. (Default: 2048)	"""

    num_gpu: Optional[int] = None
    """The number of GPUs to use. On macOS it defaults to 1 to
    enable metal support, 0 to disable."""

    num_thread: Optional[int] = None
    """Sets the number of threads to use during computation.
    By default, Ollama will detect this for optimal performance.
    It is recommended to set this value to the number of physical
    CPU cores your system has (as opposed to the logical number of cores)."""

    repeat_last_n: Optional[int] = None
    """Sets how far back for the model to look back to prevent
    repetition. (Default: 64, 0 = disabled, -1 = num_ctx)"""

    repeat_penalty: Optional[float] = None
    """Sets how strongly to penalize repetitions. A higher value (e.g., 1.5)
    will penalize repetitions more strongly, while a lower value (e.g., 0.9)
    will be more lenient. (Default: 1.1)"""

    temperature: Optional[float] = None
    """The temperature of the model. Increasing the temperature will
    make the model answer more creatively. (Default: 0.8)"""

    stop: Optional[List[str]] = None
    """Sets the stop tokens to use."""

    tfs_z: Optional[float] = None
    """Tail free sampling is used to reduce the impact of less probable
    tokens from the output. A higher value (e.g., 2.0) will reduce the
    impact more, while a value of 1.0 disables this setting. (default: 1)"""

    top_k: Optional[int] = None
    """Reduces the probability of generating nonsense. A higher value (e.g. 100)
    will give more diverse answers, while a lower value (e.g. 10)
    will be more conservative. (Default: 40)"""

    top_p: Optional[int] = None
    """Works together with top-k. A higher value (e.g., 0.95) will lead
    to more diverse text, while a lower value (e.g., 0.5) will
    generate more focused and conservative text. (Default: 0.9)"""

    show_progress: bool = False
    """Whether to show a tqdm progress bar. Must have `tqdm` installed."""

    @property
    def _default_params(self) -> Dict[str, Any]:
        """Get the default parameters for calling Ollama."""
        return {
            "model": self.model,
            "options": {
                "mirostat": self.mirostat,
                "mirostat_eta": self.mirostat_eta,
                "mirostat_tau": self.mirostat_tau,
                "num_ctx": self.num_ctx,
                "num_gpu": self.num_gpu,
                "num_thread": self.num_thread,
                "repeat_last_n": self.repeat_last_n,
                "repeat_penalty": self.repeat_penalty,
                "temperature": self.temperature,
                "stop": self.stop,
                "tfs_z": self.tfs_z,
                "top_k": self.top_k,
                "top_p": self.top_p,
            },
        }

    model_kwargs: Optional[dict] = None
    """Other model keyword args"""

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {**{"model": self.model}, **self._default_params}

    class Config:
        """Configuration for this pydantic object."""

        extra = Extra.forbid

    def _process_emb_response(self, input: str) -> List[float]:
        """Process a response from the API.

        Args:
            response: The response from the API.

        Returns:
            The response as a dictionary.
        """

        try:            
            bearer_token = get_token('ollama-server')
            res = requests.post(
                url=f"{self.base_url}/api/embeddings",
                headers={
                    "Content-Type": "application/json",
                    "AI-Resource-Group": RESOURCE_GROUP,
                    "Authorization": bearer_token
                },
                json={"model": self.model, "prompt": input, **self._default_params},
            )
        except requests.exceptions.RequestException as e:
            raise ValueError(f"Error raised by inference endpoint: {e}")

        if res.status_code != 200:
            raise ValueError(
                "Error raised by inference API HTTP code: %s, %s"
                % (res.status_code, res.text)
            )
        try:
            t = res.json()
            return t["embedding"]
        except requests.exceptions.JSONDecodeError as e:
            raise ValueError(
                f"Error raised by inference API: {e}.\nResponse: {res.text}"
            )

    def _embed(self, input: List[str]) -> List[List[float]]:
        if self.show_progress:
            try:
                from tqdm import tqdm

                iter_ = tqdm(input, desc="OllamaEmbeddings")
            except ImportError:
                logger.warning(
                    "Unable to show progress bar because tqdm could not be imported. "
                    "Please install with `pip install tqdm`."
                )
                iter_ = input
        else:
            iter_ = input
        return [self._process_emb_response(prompt) for prompt in iter_]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed documents using an Ollama deployed embedding model.

        Args:
            texts: The list of texts to embed.

        Returns:
            List of embeddings, one for each text.
        """
        instruction_pairs = [f"{self.embed_instruction}{text}" for text in texts]
        embeddings = self._embed(instruction_pairs)
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embed a query using a Ollama deployed embedding model.

        Args:
            text: The text to embed.

        Returns:
            Embeddings for the text.
        """
        instruction_pair = f"{self.query_instruction}{text}"
        embedding = self._embed([instruction_pair])[0]
        return embedding