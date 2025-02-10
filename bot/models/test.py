import os
from groq_model import GroqModel
from dotenv import load_dotenv
from openai import OpenAIModel
load_dotenv()

from openai_model import OpenAIModel  # Make sure the filename matches your OpenAI model class file

def test_openai_model():
    # Initialize the model
    model = OpenAIModel(
        model="gpt-3.5-turbo",
        system_prompt="You are a helpful assistant",
        temperature=0.7
    )
    
    # Test with raw prompt
    print("\nTesting with raw prompt:")
    response1, info1 = model.generate_text("Tell me a joke")
    print("\nRaw prompt test completed!")
    
    # Test with template
    print("\nTesting with template:")
    template = "Tell me a {type} joke about {subject}"
    response2, info2 = model.generate_text(
        prompt="",  # Not used when template is provided
        template=template,
        input_variables=["type", "subject"],
        type="funny",
        subject="programming"
    )
    print("\nTemplate test completed!")
    
    # Return both test results
    return {
        "raw_prompt_test": {"response": response1, "info": info1},
        "template_test": {"response": response2, "info": info2}
    }

if __name__ == "__main__":
    try:
        results = test_openai_model()
        print("\nAll tests completed successfully!")
    except Exception as e:
        print(f"\nError occurred during testing: {str(e)}")