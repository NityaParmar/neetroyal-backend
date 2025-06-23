import requests
import json

# Test the question bank endpoint with 50 questions
def test_question_bank():
    url = "http://127.0.0.1:5000/generate_question_bank"
    
    # Test data - requesting 50 questions on Physics (Hard difficulty)
    data = {
        "topic": "Physics",
        "difficulty": "Hard",
        "count": 50
    }
    
    print("🚀 Testing Question Bank Generation...")
    print(f"📚 Topic: {data['topic']}")
    print(f"🎯 Difficulty: {data['difficulty']}")
    print(f"📊 Requesting: {data['count']} questions")
    print("⏳ Please wait, this may take a moment...")
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            print("\n✅ SUCCESS! Question Bank Generated!")
            print(f"📈 Total Questions: {result['total_questions']}")
            print(f"📝 Topic: {result['topic']}")
            print(f"🎯 Difficulty: {result['difficulty']}")
            
            # Show first 3 questions as preview
            print("\n📋 Preview (First 3 Questions):")
            for i, question in enumerate(result['questions'][:3], 1):
                print(f"\n--- Question {i} ---")
                print(f"Q: {question['question']}")
                for option in question['options']:
                    print(f"   {option}")
                print(f"✅ Answer: {question['answer']}")
            
            if len(result['questions']) > 3:
                print(f"\n... and {len(result['questions']) - 3} more questions!")
            
            # Save to file for easy viewing
            with open('question_bank_output.json', 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Full question bank saved to: question_bank_output.json")
            
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Make sure your Flask server is running!")
        print("Run: python app.py")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    test_question_bank() 