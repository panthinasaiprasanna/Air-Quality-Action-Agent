"""
IBM Granite LLM Client
Handles all interactions with IBM watsonx.ai using IBM Granite models
"""
import os
import warnings
from dotenv import load_dotenv

load_dotenv()

# Suppress known harmless SDK warnings
warnings.filterwarnings("ignore", category=UserWarning, message=".*max_new_tokens.*")
warnings.filterwarnings("ignore", message=".*deprecated.*", category=DeprecationWarning)

# Try to import IBM watsonx AI
try:
    from ibm_watsonx_ai import Credentials
    from ibm_watsonx_ai.foundation_models import ModelInference
    from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    IBM_WATSONX_AVAILABLE = True
except ImportError:
    IBM_WATSONX_AVAILABLE = False


class GraniteClient:
    """IBM Granite LLM client for generating AI-powered insights"""

    def __init__(self):
        self.api_key = os.getenv("IBM_CLOUD_API_KEY", "")
        self.project_id = os.getenv("IBM_WATSONX_PROJECT_ID", "")
        self.url = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
        self.model = None
        self._initialized = False

        if IBM_WATSONX_AVAILABLE and self.api_key and self.project_id:
            self._init_model()

    def _init_model(self):
        """Initialize the IBM Granite model"""
        try:
            credentials = Credentials(
                url=self.url,
                api_key=self.api_key
            )
            self.model = ModelInference(
                model_id="ibm/granite-4-h-small",
                credentials=credentials,
                project_id=self.project_id,
                params={
                    GenParams.TEMPERATURE: 0.7,
                    GenParams.TOP_P: 0.9,
                }
            )
            self._initialized = True
            print("✓ IBM Granite 4-H Small model initialized successfully")
        except Exception as e:
            print(f"⚠ IBM Granite initialization failed: {e}")
            self._initialized = False

    def generate(self, prompt: str, max_tokens: int = 512) -> str:
        """
        Generate text using IBM Granite model via chat API.
        Falls back to rule-based responses if IBM watsonx is unavailable.
        """
        if self._initialized and self.model:
            try:
                messages = [
                    {
                        "role": "system",
                        "content": (
                            "You are an expert air quality and public health advisor. "
                            "Provide concise, accurate, and actionable responses. "
                            "Always be specific and practical."
                        )
                    },
                    {"role": "user", "content": prompt}
                ]
                response = self.model.chat(messages=messages)
                text = response["choices"][0]["message"]["content"].strip()
                return text if text else self._fallback_response(prompt)
            except Exception as e:
                print(f"⚠ Granite generation error: {e}")
                return self._fallback_response(prompt)
        else:
            return self._fallback_response(prompt)

    def _fallback_response(self, prompt: str) -> str:
        """
        Rule-based fallback when IBM Granite is unavailable.
        Produces structured responses based on prompt context.
        """
        prompt_lower = prompt.lower()

        if "health" in prompt_lower and "recommendation" in prompt_lower:
            return (
                "Based on current air quality conditions, here are personalized health recommendations: "
                "Stay indoors during peak pollution hours (morning and evening). "
                "Use N95 masks if outdoor activity is necessary. "
                "Keep windows closed and use air purifiers indoors. "
                "Stay hydrated and avoid strenuous outdoor exercise. "
                "Monitor symptoms like coughing or shortness of breath."
            )
        elif "forecast" in prompt_lower or "predict" in prompt_lower:
            return (
                "Air quality forecast analysis: Based on historical patterns and current meteorological conditions, "
                "expect moderate to poor air quality over the next 48 hours. "
                "Wind speeds are expected to decrease, reducing pollutant dispersion. "
                "Consider postponing outdoor activities and stock up on protective masks. "
                "Air quality is expected to improve by day 3 as wind patterns shift."
            )
        elif "community" in prompt_lower or "policy" in prompt_lower:
            return (
                "Community action recommendations: Organize neighborhood carpooling to reduce vehicular emissions. "
                "Advocate for stricter industrial emission controls with local authorities. "
                "Promote green spaces and tree planting drives. "
                "Raise awareness through social media campaigns about AQI impacts. "
                "Coordinate with schools to adjust outdoor activities on high-pollution days."
            )
        elif "summary" in prompt_lower or "report" in prompt_lower:
            return (
                "Daily Air Quality Summary: Today's air quality requires attention. "
                "Sensitive groups including elderly, children, and those with respiratory conditions "
                "should limit outdoor exposure. General public should reduce prolonged outdoor exertion. "
                "Key pollutants: PM2.5 and PM10 are the primary concerns today. "
                "Recommend monitoring AQI updates throughout the day."
            )
        else:
            return (
                "Air quality advisory: Current conditions require caution. "
                "Follow local health authority guidelines and stay informed about AQI levels. "
                "Protective measures are advised for sensitive population groups."
            )

    def is_available(self) -> bool:
        """Check if IBM Granite is available"""
        return self._initialized


# Singleton instance
granite_client = GraniteClient()
