"""
Minimal Chat Flow Emulator
==========================

This script emulates the complete chat flow with minimal code:
1. Chat initialization
2. STT (Speech-to-Text)
3. Chat processing with fact-checking
4. TTS (Text-to-Speech)
5. Conversation evaluation

Based on the existing APIs in your system.
"""

import asyncio
import aiohttp
import json
import base64
import sys
import io
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from uuid import uuid4

class ConsoleCapture:
    def __init__(self, emulator):
        self.emulator = emulator
        self.original_stdout = sys.stdout
        
    def write(self, text):
        self.original_stdout.write(text)
        if '🔢' in text:  # Token usage indicator
            self.emulator.track_console_output(text)
        
    def flush(self):
        self.original_stdout.flush()

class ChatFlowEmulator:
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
        self.session_id = None
        self.conversation_count = 0
        self.token_tracker = []
        self.total_cost = 0.0
        
        # Configuration - replace with actual values
        self.config = {
            "avatar_interaction_id": "d9ce8d3a-2298-462a-b5c0-74fc8e5d575e",
            "mode": "try_mode",  # learn_mode, try_mode, assess_mode
            "persona_id": "66a514de-de0c-4f23-ac3f-b0bb18909861",
            "avatar_id": "4868681f-117b-45a3-b5db-b083f7015f35", 
            "language_id": "ec489817-553a-4ef4-afb5-154f78f041b6",
            "voice_id": "ar-SA-HamedNeural"
        }
           
        # Auth token - REQUIRED for all APIs
        self.auth_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI4YjIzODQ5Ny04YmIzLTQ5YjAtYWU2Ny01ZTgyZjJhY2IxYzUiLCJyb2xlIjoidXNlciIsImNvbXBhbnlfaWQiOiJkNGIyYzJmZi1jNThhLTQ5ODEtYTRhMC01NGIwNGE3MWUzYjQiLCJleHAiOjE3NTgxNjgwNjh9.9ngZLRSaOv4MKHXp9YvXLKSbb5UTVxivi1jgicyO2i8"  # Replace with actual token
        self.headers = {"Authorization": f"Bearer {self.auth_token}"}

    async def run_complete_flow(self):
        """Run the complete chat flow with 20 audio files"""
        print("🚀 Starting Complete Chat Flow Emulation with 20 Audio Files")
        
        # Get 20 audio files from audio_files directory
        audio_dir = Path("audio_files")
        if not audio_dir.exists():
            print("❌ audio_files directory not found")
            return
            
        audio_files = sorted(list(audio_dir.glob("*.wav")))[:20]
        if len(audio_files) < 20:
            print(f"❌ Found only {len(audio_files)} audio files, need 20")
            return
            
        print(f"✅ Found {len(audio_files)} audio files")
        
        # Capture console output to track token usage
        console_capture = ConsoleCapture(self)
        original_stdout = sys.stdout
        sys.stdout = console_capture
        
        try:
            async with aiohttp.ClientSession() as session:
                # Step 1: Initialize Chat Session
                await self.initialize_chat_session(session)
                
                # Step 2: Process 20 audio conversations
                await self.process_audio_conversations(session, audio_files)
                
                # Step 3: Evaluate the conversation
                await self.evaluate_conversation(session)
                
                # Step 4: Calculate total costs from tracked tokens
                self.calculate_total_costs()
        finally:
            sys.stdout = original_stdout
            
        print("✅ Complete Chat Flow Emulation Finished")

    async def initialize_chat_session(self, session: aiohttp.ClientSession):
        """Initialize chat session with avatar interaction"""
        print("\n📋 Step 1: Initializing Chat Session")
        
        try:
            data = aiohttp.FormData()
            data.add_field('avatar_interaction_id', self.config["avatar_interaction_id"])
            data.add_field('mode', self.config["mode"])
            data.add_field('persona_id', self.config["persona_id"])
            data.add_field('avatar_id', self.config["avatar_id"])
            data.add_field('language_id', self.config["language_id"])
            
            async with session.post(f"{self.base_url}/chat/initialize", data=data, headers=self.headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    self.session_id = result.get("id")
                    print(f"✅ Chat session initialized: {self.session_id}")
                    print(f"   Scenario: {result.get('scenario_name')}")
                    print(f"   Mode: {result.get('mode')}")
                else:
                    print(f"❌ Chat initialization failed: {resp.status}")
                    text = await resp.text()
                    print(f"   Error: {text}")
                    
        except Exception as e:
            print(f"❌ Chat initialization error: {e}")

    async def process_audio_conversations(self, session: aiohttp.ClientSession, audio_files: List[Path]):
        """Process real audio files through the complete flow"""
        print(f"\n🎵 Step 2: Processing {len(audio_files)} Audio Conversations")
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n--- Conversation {i}/{len(audio_files)}: {audio_file.name} ---")
            
            # STT: Convert audio to text
            user_text = await self.speech_to_text(session, audio_file)
            if not user_text:
                user_text = f"Mock user input {i}"
            
            # Chat: Process user message and get AI response
            ai_response = await self.process_chat_message(session, user_text)
            if not ai_response:
                ai_response = f"Mock AI response to: {user_text}"
            
            # TTS: Convert AI response to audio
            await self.text_to_speech(session, ai_response, f"response_{i}.wav")
            
            self.conversation_count += 1



    async def speech_to_text(self, session: aiohttp.ClientSession, audio_file: Path) -> Optional[str]:
        """Convert audio file to text using STT API"""
        try:
            with open(audio_file, 'rb') as f:
                data = aiohttp.FormData()
                data.add_field('file', f, filename=audio_file.name, content_type='audio/wav')
                data.add_field('language_code', 'en-US')
                
                async with session.post(f"{self.base_url}/speech/stt", data=data) as resp:
                    if resp.status == 200:
                        result = await resp.json()
                        text = result.get("text", "").strip()
                        print(f"🎤 STT: {text}")
                        return text
                    else:
                        print(f"❌ STT failed: {resp.status}")
                        
        except Exception as e:
            print(f"❌ STT error: {e}")
        
        return None

    async def process_chat_message(self, session: aiohttp.ClientSession, message: str) -> Optional[str]:
        """Process chat message through the complete pipeline"""
        if not self.session_id:
            print("❌ No session ID available")
            return None
        
        try:
            # Send chat message
            data = aiohttp.FormData()
            data.add_field('message', message)
            data.add_field('id', self.session_id)
            
            async with session.post(f"{self.base_url}/chat", data=data, headers=self.headers) as resp:
                if resp.status != 200:
                    print(f"❌ Chat message failed: {resp.status}")
                    return None
            
            # Get streaming response
            return await self.get_streaming_response(session)
            
        except Exception as e:
            print(f"❌ Chat processing error: {e}")
            return None

    async def get_streaming_response(self, session: aiohttp.ClientSession) -> Optional[str]:
        """Get streaming chat response with fact-checking"""
        try:
            async with session.get(f"{self.base_url}/chat/stream?id={self.session_id}", headers=self.headers) as resp:
                if resp.status != 200:
                    print(f"❌ Stream failed: {resp.status}")
                    return None
                
                full_response = ""
                fact_check_info = None
                
                async for line in resp.content:
                    if line:
                        chunk = line.decode().strip()
                        if chunk.startswith("data: "):
                            chunk_data = chunk[6:]
                            if chunk_data != "[DONE]":
                                try:
                                    data = json.loads(chunk_data)
                                    
                                    if "response" in data:
                                        full_response = data["response"]
                                    
                                    if data.get("fact_check_summary"):
                                        fact_check_info = data["fact_check_summary"]
                                        print(f"🔍 Fact-check: {fact_check_info}")
                                    
                                    if data.get("complete"):
                                        break
                                        
                                except json.JSONDecodeError:
                                    continue
                
                print(f"🤖 AI Response: {full_response[:100]}...")
                return full_response
                
        except Exception as e:
            print(f"❌ Streaming error: {e}")
            return None

    async def text_to_speech(self, session: aiohttp.ClientSession, text: str, filename: str):
        """Convert text to speech using TTS API"""
        try:
            data = aiohttp.FormData()
            data.add_field('message', text)
            data.add_field('voice_id', self.config["voice_id"])
            
            async with session.post(f"{self.base_url}/speech/tts", data=data) as resp:
                if resp.status == 200:
                    audio_data = await resp.read()
                    
                    # Save audio file
                    output_path = Path("generated_audio") / filename
                    output_path.parent.mkdir(exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        f.write(audio_data)
                    
                    print(f"🔊 TTS saved: {filename}")
                else:
                    print(f"❌ TTS failed: {resp.status}")
                    
        except Exception as e:
            print(f"❌ TTS error: {e}")

    async def evaluate_conversation(self, session: aiohttp.ClientSession):
        """Evaluate the complete conversation"""
        if not self.session_id:
            print("❌ No session ID for evaluation")
            return
        
        print(f"\n📊 Step 3: Evaluating Conversation (Session: {self.session_id})")
        
        try:
            async with session.post(f"{self.base_url}/chat/evaluate/{self.session_id}", headers=self.headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    
                    print("✅ Conversation Evaluation Results:")
                    print(f"   Overall Score: {result.get('score', 'N/A')}")
                    print(f"   Mode: {result.get('mode', 'N/A')}")
                    
                    evaluation = result.get('evaluation', {})
                    if evaluation:
                        print(f"   Performance: {evaluation.get('performance_category', 'N/A')}")
                        print(f"   Factual Accuracy: {evaluation.get('factual_accuracy', 'N/A')}")
                        
                        strengths = evaluation.get('strengths', [])
                        if strengths:
                            print(f"   Strengths: {', '.join(strengths[:2])}")
                        
                        improvements = evaluation.get('areas_for_improvement', [])
                        if improvements:
                            print(f"   Areas for Improvement: {', '.join(improvements[:2])}")
                    
                else:
                    print(f"❌ Evaluation failed: {resp.status}")
                    error_text = await resp.text()
                    print(f"   Error: {error_text}")
                    
        except Exception as e:
            print(f"❌ Evaluation error: {e}")

    def track_console_output(self, line):
        """Parse token usage from console output"""
        import re
        
        # Look for token usage patterns from log_token_usage
        pattern = r'🔢 (\w+): (\d+) tokens \(prompt: (\d+), completion: (\d+)\)'
        match = re.search(pattern, line)
        
        if match:
            operation = match.group(1)
            total_tokens = int(match.group(2))
            prompt_tokens = int(match.group(3))
            completion_tokens = int(match.group(4))
            
            # Calculate cost
            input_cost = (prompt_tokens / 1_000_000) * 2.50
            output_cost = (completion_tokens / 1_000_000) * 10.00
            total_cost = input_cost + output_cost
            
            self.token_tracker.append({
                'operation': operation,
                'total_tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens,
                'cost': total_cost
            })
            
            self.total_cost += total_cost
            print(f"💰 Tracked {operation}: ${total_cost:.4f}")
    
    def calculate_total_costs(self):
        """Calculate and display total costs"""
        print(f"\n💰 Step 4: Total Cost Summary")
        
        if self.token_tracker:
            total_tokens = sum(t['total_tokens'] for t in self.token_tracker)
            print(f"✅ All API Calls Tracked:")
            print(f"   Total Operations: {len(self.token_tracker)}")
            print(f"   Total Tokens: {total_tokens:,}")
            print(f"   Total Cost: ${self.total_cost:.4f}")
            
            # Show breakdown
            operations = {}
            for t in self.token_tracker:
                op = t['operation']
                if op not in operations:
                    operations[op] = {'count': 0, 'tokens': 0, 'cost': 0.0}
                operations[op]['count'] += 1
                operations[op]['tokens'] += t['total_tokens']
                operations[op]['cost'] += t['cost']
            
            print("\n   Breakdown by Operation:")
            for op, stats in operations.items():
                print(f"     {op}: {stats['count']} calls, {stats['tokens']} tokens, ${stats['cost']:.4f}")
        else:
            print("⚠️  No token usage tracked - check console output manually")

    def print_summary(self):
        """Print execution summary"""
        print("\n" + "="*60)
        print("🎯 CHAT FLOW EMULATION SUMMARY")
        print("="*60)
        print(f"📋 Session ID: {self.session_id}")
        print(f"💬 Conversations Processed: {self.conversation_count}")
        print(f"🎵 Audio Files Generated: {len(list(Path('generated_audio').glob('*.wav')) if Path('generated_audio').exists() else [])}")
        print(f"⚙️  Mode: {self.config['mode']}")
        print(f"🤖 Avatar Interaction: {self.config['avatar_interaction_id']}")
        
        # Cost summary
        if self.token_tracker:
            total_tokens = sum(t['total_tokens'] for t in self.token_tracker)
            print(f"💰 Total Session Cost: ${self.total_cost:.4f}")
            print(f"🎫 Total Tokens Used: {total_tokens:,}")
            print(f"📞 Total API Calls: {len(self.token_tracker)}")
        
        print("="*60)

# Standalone API Flow Tester
class APIFlowTester:
    """Test individual API endpoints"""
    
    def __init__(self, base_url: str = "http://localhost:9000"):
        self.base_url = base_url
    
    async def test_all_apis(self):
        """Test all chat-related APIs"""
        print("🧪 Testing Individual APIs")
        
        async with aiohttp.ClientSession() as session:
            # Test STT
            await self.test_stt_api(session)
            
            # Test TTS
            await self.test_tts_api(session)
            
            # Test Chat Initialize
            await self.test_chat_initialize(session)

    async def test_stt_api(self, session: aiohttp.ClientSession):
        """Test STT API with mock audio"""
        print("\n🎤 Testing STT API")
        
        # Create a minimal WAV file for testing
        mock_wav_data = self.create_mock_wav()
        
        try:
            data = aiohttp.FormData()
            data.add_field('file', mock_wav_data, filename='test.wav', content_type='audio/wav')
            data.add_field('language_code', 'en-US')
            
            async with session.post(f"{self.base_url}/speech/stt", data=data) as resp:
                print(f"STT API Status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"STT Result: {result}")
                else:
                    error = await resp.text()
                    print(f"STT Error: {error}")
                    
        except Exception as e:
            print(f"STT Test Error: {e}")

    async def test_tts_api(self, session: aiohttp.ClientSession):
        """Test TTS API"""
        print("\n🔊 Testing TTS API")
        
        try:
            data = aiohttp.FormData()
            data.add_field('message', 'Hello, this is a test message')
            data.add_field('voice_id', 'en-US-AriaNeural')
            
            async with session.post(f"{self.base_url}/speech/tts", data=data) as resp:
                print(f"TTS API Status: {resp.status}")
                if resp.status == 200:
                    audio_data = await resp.read()
                    print(f"TTS Result: Received {len(audio_data)} bytes of audio")
                else:
                    error = await resp.text()
                    print(f"TTS Error: {error}")
                    
        except Exception as e:
            print(f"TTS Test Error: {e}")

    async def test_chat_initialize(self, session: aiohttp.ClientSession):
        """Test Chat Initialize API"""
        print("\n📋 Testing Chat Initialize API")
        
        try:
            data = aiohttp.FormData()
            data.add_field('avatar_interaction_id', 'f47ac10b-58cc-4372-a567-0e02b2c3d479')
            data.add_field('mode', 'try_mode')
            
            async with session.post(f"{self.base_url}/chat/initialize", data=data) as resp:
                print(f"Chat Initialize Status: {resp.status}")
                if resp.status == 200:
                    result = await resp.json()
                    print(f"Chat Initialize Result: {result}")
                else:
                    error = await resp.text()
                    print(f"Chat Initialize Error: {error}")
                    
        except Exception as e:
            print(f"Chat Initialize Test Error: {e}")

    def create_mock_wav(self) -> bytes:
        """Create a minimal WAV file for testing"""
        # Minimal WAV header + silence
        wav_header = b'RIFF$\x00\x00\x00WAVEfmt \x10\x00\x00\x00\x01\x00\x01\x00D\xac\x00\x00\x88X\x01\x00\x02\x00\x10\x00data\x00\x00\x00\x00'
        return wav_header

# Main execution functions
async def run_full_emulation():
    """Run complete chat flow emulation with 20 audio files"""
    emulator = ChatFlowEmulator()
    await emulator.run_complete_flow()
    emulator.print_summary()

async def run_api_tests():
    """Run individual API tests"""
    tester = APIFlowTester()
    await tester.test_all_apis()

async def main():
    """Main function - choose what to run"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        await run_api_tests()
    else:
        await run_full_emulation()

if __name__ == "__main__":
    print("🚀 Minimal Chat Flow Emulator - 20 Audio Files")
    print("⚠️  IMPORTANT: Update YOUR_BEARER_TOKEN_HERE with actual token")
    print("💰 Cost Tracking: Watch console for token usage from log_token_usage()")
    print("Usage:")
    print("  python minimal_chat_flow_emulator.py        # Run with 20 audio files")
    print()
    
    asyncio.run(main())