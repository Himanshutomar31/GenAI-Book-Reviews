from openai import AzureOpenAI
import fitz 
from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_DEPLOYMENT_NAME

def extract_text_from_pdf(pdf_path):
    """
    Extracts text from a PDF file.
    """
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text

def generate_summary(text):
    """
    Uses Azure OpenAI GPT-4 to generate a summary of the given text.
    """
    client = AzureOpenAI(
                azure_endpoint=AZURE_OPENAI_ENDPOINT,
                api_key=AZURE_OPENAI_API_KEY,
                api_version="2024-05-01-preview",
            )

    chat_prompt=[{"role": "system", "content": "Summarize the following book content."},
            {"role": "user", "content": text}]

    completion = client.chat.completions.create(
            model=AZURE_OPENAI_DEPLOYMENT_NAME,
            messages=chat_prompt,
            max_tokens=300,
            temperature=0,
            top_p=0.95,
            frequency_penalty=0,
            presence_penalty=0,
            stop=None,
            stream=False,
    )

    return  completion.choices[0].message.content
