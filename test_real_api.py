"""
Real API integration test - Tests actual coaching through running FastAPI server
Server must be running on http://localhost:9000
"""

import asyncio
import httpx
import json

BASE_URL = "http://172.23.198.149:9000/api"
BEARER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJiYTdiM2MxNi03ZDVhLTRmMjktYjQ0NS1mMmIyNWMxYmY3NDYiLCJyb2xlIjoidXNlciIsImNvbXBhbnlfaWQiOiJkNGIyYzJmZi1jNThhLTQ5ODEtYTRhMC01NGIwNGE3MWUzYjQiLCJleHAiOjE3NjI1MTYxMTV9.Q9HIEppmSCFOs2G3uFSYj8tzRyBdz0HUNkZk7tIOees"
AVATAR_INTERACTION_ID = "YOUR_AVATAR_INTERACTION_ID_HERE"  # Paste your avatar_interaction_id

# Test messages that should trigger coaching
TEST_MESSAGES = [
    {
        "name": "Wrong Product",
        "message": "I recommend Product X for irregular bleeding",
        "should_coach": True,
        "reason": "Wrong product name"
    },
    {
        "name": "Vague Claim",
        "message": "Here's some product info",
        "should_coach": True,
        "reason": "Too vague"
    },
    {
        "name": "Abuse",
        "message": "This is donkey stupid",
        "should_coach": True,
        "reason": "Contains abuse"
    },
    {
        "name": "Wrong Percentage",
        "message": "EO-Dine reduces bleeding by 30%",
        "should_coach": True,
        "reason": "Wrong percentage (should be 60%)"
    }
]

async def login():
    """Use hardcoded bearer token"""
    print("\n" + "="*80)
    print("STEP 1: USING BEARER TOKEN")
    print("="*80)
    print(f"Token: {BEARER_TOKEN[:50]}...")
    return BEARER_TOKEN

async def get_try_mode_avatar_interaction(token):
    """Use hardcoded avatar_interaction_id"""
    print("\n" + "="*80)
    print("STEP 2: USING AVATAR INTERACTION ID")
    print("="*80)
    print(f"Avatar Interaction: {AVATAR_INTERACTION_ID}")
    return AVATAR_INTERACTION_ID

async def initialize_chat_session(token, avatar_interaction_id):
    """Initialize a chat session"""
    print("\n" + "="*80)
    print("STEP 3: INITIALIZE CHAT SESSION")
    print("="*80)
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        response = await client.post(
            f"{BASE_URL}/chat/initialize",
            headers=headers,
            json={
                "avatar_interaction_id": avatar_interaction_id,
                "mode": "try_mode"
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("id")
            print(f"[SUCCESS] Session created: {session_id}")
            return session_id
        else:
            print(f"[FAIL] Could not create session: {response.status_code}")
            print(response.text)
            return None

async def send_message_and_check_coaching(token, session_id, test_case):
    """Send a message and check if coaching appears"""
    print("\n" + "-"*80)
    print(f"TEST: {test_case['name']}")
    print("-"*80)
    print(f"Message: '{test_case['message']}'")
    print(f"Expected: {test_case['reason']}")
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Send message
        response = await client.post(
            f"{BASE_URL}/chat",
            headers=headers,
            json={
                "message": test_case['message'],
                "id": session_id
            }
        )
        
        if response.status_code != 200:
            print(f"[FAIL] Could not send message: {response.status_code}")
            return False
        
        # Get streaming response
        full_response = ""
        coaching_detected = False
        
        async with client.stream(
            "GET",
            f"{BASE_URL}/chat/stream?id={session_id}",
            headers=headers
        ) as stream_response:
            async for line in stream_response.aiter_lines():
                if line.startswith("data: "):
                    try:
                        data = json.loads(line[6:])
                        response_text = data.get("response", "")
                        full_response = response_text
                        
                        # Check for coaching markers
                        if any(marker in response_text for marker in ["[CORRECT]", "Dear Learner", "Factual Correction", "inappropriate language"]):
                            coaching_detected = True
                    except:
                        pass
        
        print(f"\n{'='*80}")
        print("RESPONSE:")
        print(f"{'='*80}")
        print(full_response[:500] + ("..." if len(full_response) > 500 else ""))
        print(f"{'='*80}")
        
        if coaching_detected:
            print(f"\n[PASS] Coach appeared as expected!")
            
            # Check for specific issues
            if "[CORRECT]" in full_response:
                print("  - [CORRECT] tags present")
            if "Dear Learner" in full_response:
                print("  - 'Dear Learner' format used")
            if "inappropriate language" in full_response.lower():
                print("  - Abuse warning given")
            
            # Check message length
            if "[CORRECT]" in full_response:
                coaching_parts = full_response.split("[CORRECT]")
                if len(coaching_parts) >= 2:
                    coaching_text = coaching_parts[1]
                    word_count = len(coaching_text.split())
                    print(f"  - Coaching length: {word_count} words")
                    if word_count <= 50:
                        print("  - [PASS] Concise (<=50 words)")
                    else:
                        print(f"  - [WARN] Too long ({word_count} words)")
        else:
            print(f"\n[INFO] No coaching detected")
            if test_case['should_coach']:
                print(f"  [WARN] Expected coaching but didn't get it")
        
        return coaching_detected

async def run_real_api_test():
    """Run complete API integration test"""
    print("\n" + "="*80)
    print("REAL API INTEGRATION TEST")
    print("Testing against: http://localhost:9000")
    print("="*80)
    
    # Step 1: Login
    token = await login()
    if not token:
        print("\n[FAIL] Cannot proceed without authentication")
        return
    
    # Step 2: Use avatar interaction
    avatar_interaction_id = await get_try_mode_avatar_interaction(token)
    
    # Step 3: Initialize session
    session_id = await initialize_chat_session(token, avatar_interaction_id)
    if not session_id:
        print("\n[FAIL] Cannot proceed without session")
        return
    
    # Step 4: Test each message
    print("\n" + "="*80)
    print("STEP 4: TESTING COACHING SCENARIOS")
    print("="*80)
    
    results = []
    for test_case in TEST_MESSAGES:
        coaching_detected = await send_message_and_check_coaching(token, session_id, test_case)
        results.append({
            "test": test_case['name'],
            "coaching_detected": coaching_detected,
            "expected": test_case['should_coach']
        })
        
        # Wait between messages
        await asyncio.sleep(3)
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for result in results:
        status = "[PASS]" if result['coaching_detected'] == result['expected'] else "[FAIL]"
        coach_status = "COACHED" if result['coaching_detected'] else "NO COACH"
        print(f"{status} {result['test']}: {coach_status}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("\nStarting Real API Integration Test...")
    print("Make sure FastAPI server is running on http://localhost:9000")
    print("\nPress Ctrl+C to cancel\n")
    
    try:
        asyncio.run(run_real_api_test())
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
    except Exception as e:
        print(f"\n\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
