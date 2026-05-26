import os
from dotenv import load_dotenv
from google import genai

# 👇 CARGA EL .env
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

client = genai.Client(api_key=API_KEY)


def main():
    try:
        print("🚀 Probando Gemini...\n")

        models = client.models.list()
        print("📌 MODELOS DISPONIBLES:")
        for m in models:
            print("-", m.name)

        response = client.models.generate_content(
            model="gemini-flash-latest",
            contents="Dime un dato curioso sobre las papas"
        )

        print("\n=== RESPUESTA ===\n")
        print(response.text)

    except Exception as e:
        print("\n❌ ERROR:\n")
        print(e)


if __name__ == "__main__":
    main()