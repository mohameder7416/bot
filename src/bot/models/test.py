import os
from ollama_model import OllamaModel
from dotenv import load_dotenv

load_dotenv()

def test_ollama_model():
    # Initialize the model
    model = OllamaModel(
        model="phi4",  # You can replace with your preferred model
        system_prompt="You are a helpful assistant",
        temperature=0.7
    )
    
    # Test with raw prompt
    print("\nTesting with raw prompt:")
    response1 = model.generate_text("Tell me a joke")
    print("\nRaw prompt test completed!")
    
    # Test with template
    # Note: The current OllamaModel implementation doesn't support templates directly
    # So we'll create a template-like functionality here for testing
    print("\nTesting with template-like functionality:")
    type_of_joke = "funny"
    subject = "programming"
    template_prompt = f"Tell me a {type_of_joke} joke about {subject}"
    response2 = model.generate_text(template_prompt)
    print("\nTemplate-like test completed!")
    
    # Return both test results
    return {
        "raw_prompt_test": {"response": response1},
        "template_test": {"response": response2}
    }

if __name__ == "__main__":
    try:
        results = test_ollama_model()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError occurred during testing: {str(e)}")