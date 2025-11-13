"""
Proveedor unificado de LLMs con soporte para Claude, OpenAI y Gemini.
"""
import os
from typing import Generator, Optional
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path, override=True)

# Intentar importar streamlit para acceso a secrets
try:
    import streamlit as st
    STREAMLIT_AVAILABLE = True
except ImportError:
    STREAMLIT_AVAILABLE = False


class LLMProvider:
    """
    Proveedor unificado de LLMs con soporte para múltiples proveedores.
    """

    def __init__(self, provider: Optional[str] = None):
        """
        Inicializa el proveedor de LLM.

        Args:
            provider: Nombre del proveedor ('claude', 'openai', 'gemini')
                     Si es None, usa LLM_PROVIDER del .env
        """
        # Determinar proveedor
        self.provider = provider or self._get_env_var('LLM_PROVIDER', 'claude')
        self.provider = self.provider.lower()

        print(f"DEBUG - Inicializando LLM Provider: {self.provider}")

        # Inicializar cliente según proveedor
        if self.provider == 'claude':
            self._init_claude()
        elif self.provider == 'openai':
            self._init_openai()
        elif self.provider == 'gemini':
            self._init_gemini()
        else:
            raise ValueError(
                f"Proveedor '{self.provider}' no soportado. "
                "Usa: 'claude', 'openai' o 'gemini'"
            )

    def _get_env_var(self, key: str, default: str = '') -> str:
        """Obtiene variable de entorno de múltiples fuentes."""
        # Prioridad: Streamlit secrets > variables de entorno
        if STREAMLIT_AVAILABLE and hasattr(st, 'secrets'):
            try:
                if key in st.secrets:
                    return st.secrets[key]
            except:
                pass
        return os.getenv(key, default)

    def _init_claude(self):
        """Inicializa cliente de Claude."""
        import anthropic

        api_key = self._get_env_var('ANTHROPIC_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError(
                "API key de Claude no encontrada. "
                "Configura ANTHROPIC_API_KEY en .env o Streamlit Secrets.\n"
                "Obtén tu key en: https://console.anthropic.com/settings/keys"
            )

        self.client = anthropic.Anthropic(api_key=api_key)
        self.model_name = "claude-3-5-haiku-20241022"  # El más rápido
        print(f"✅ Claude inicializado: {self.model_name}")

    def _init_openai(self):
        """Inicializa cliente de OpenAI."""
        import openai

        api_key = self._get_env_var('OPENAI_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError(
                "API key de OpenAI no encontrada. "
                "Configura OPENAI_API_KEY en .env o Streamlit Secrets.\n"
                "Obtén tu key en: https://platform.openai.com/api-keys"
            )

        self.client = openai.OpenAI(api_key=api_key)
        self.model_name = "gpt-4o-mini"  # Rápido y económico
        print(f"✅ OpenAI inicializado: {self.model_name}")

    def _init_gemini(self):
        """Inicializa cliente de Gemini."""
        import google.generativeai as genai

        api_key = self._get_env_var('GOOGLE_API_KEY')
        if not api_key or api_key == 'your_api_key_here':
            raise ValueError(
                "API key de Gemini no encontrada. "
                "Configura GOOGLE_API_KEY en .env o Streamlit Secrets.\n"
                "Obtén tu key en: https://aistudio.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)
        self.client = genai.GenerativeModel('gemini-2.5-flash')
        self.model_name = "gemini-2.5-flash"
        print(f"✅ Gemini inicializado: {self.model_name}")

    def generate(self, prompt: str, max_tokens: int = 2048) -> str:
        """
        Genera respuesta completa (sin streaming).

        Args:
            prompt: Prompt para el modelo
            max_tokens: Máximo de tokens a generar

        Returns:
            Respuesta del modelo
        """
        try:
            if self.provider == 'claude':
                response = self.client.messages.create(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text

            elif self.provider == 'openai':
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content

            elif self.provider == 'gemini':
                response = self.client.generate_content(prompt)
                return response.text

        except Exception as e:
            return f"❌ Error al generar respuesta con {self.provider}: {str(e)}"

    def generate_stream(self, prompt: str, max_tokens: int = 2048) -> Generator[str, None, None]:
        """
        Genera respuesta con streaming.

        Args:
            prompt: Prompt para el modelo
            max_tokens: Máximo de tokens a generar

        Yields:
            Fragmentos de texto de la respuesta
        """
        try:
            if self.provider == 'claude':
                with self.client.messages.stream(
                    model=self.model_name,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                ) as stream:
                    for text in stream.text_stream:
                        yield text

            elif self.provider == 'openai':
                stream = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    stream=True
                )
                for chunk in stream:
                    if chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content

            elif self.provider == 'gemini':
                response = self.client.generate_content(prompt, stream=True)
                for chunk in response:
                    if chunk.text:
                        yield chunk.text

        except Exception as e:
            yield f"❌ Error al generar respuesta con {self.provider}: {str(e)}"

    def get_info(self) -> dict:
        """Retorna información sobre el proveedor actual."""
        return {
            'provider': self.provider,
            'model': self.model_name
        }
