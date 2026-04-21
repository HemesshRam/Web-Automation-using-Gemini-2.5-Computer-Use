from google import genai

# 1. Initialize the client with your API key
api_key = "AIzaSyDv8kZHSESg95dCFRSeNCCFKpodaLCPYqk"
client = genai.Client(api_key=api_key)

try:
    # 2. Select the current model (gemini-2.5-flash is the standard fast model)
    model_id = 'gemini-2.5-flash'

    # 3. Send the prompt using the new client syntax
    print("Sending prompt to Gemini: 'what is 2+2?'...")
    response = client.models.generate_content(
        model=model_id,
        contents="what is 2+2?"
    )

    # 4. Print the result
    print("\nGemini's Response:")
    print(response.text)

except Exception as e:
    print(f"\nError: Something went wrong.\nDetails: {e}")