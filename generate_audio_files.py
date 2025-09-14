"""
Generate audio files from text using speech.py TTS function
"""

import asyncio
import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

load_dotenv(".env")

# Try mode advisor responses
ADVISOR_RESPONSES = [
    "I understand your concern about the premium cost. Let me explain HealthGuard's value proposition compared to Star Health.",
    "That's exactly why now is the perfect time to get coverage. Medical costs are rising fifteen percent annually.",
    "HealthGuard has a ninety-four percent claim settlement ratio, which is higher than HDFC Ergo's eighty-seven percent.",
    "I can offer you a family discount and flexible payment options to make this more affordable for you.",
    "Absolutely, take your time. Let me give you a detailed comparison sheet to discuss with your family.",
    "Let me show you the additional benefits and faster claim settlement that justify our premium difference.",
    "HealthGuard offers lifetime renewability with no premium increase due to claims or age-related conditions.",
    "I understand your concern. HealthGuard has the highest claim settlement ratio in the industry at ninety-four percent.",
    "The waiting period is mandated by IRDAI, but we offer the shortest possible periods and comprehensive coverage.",
    "Company insurance has limitations. Let me explain the gaps that personal coverage fills for complete protection.",
    "We have over eight thousand five hundred network hospitals. I can check if your doctor's hospital can be added.",
    "Our co-payment is competitive, and we offer zero co-payment options for higher premium plans.",
    "HealthGuard settles claims in seven to fifteen days with the highest approval rate in the industry.",
    "Let me use our official premium calculator to give you an accurate quote based on your exact requirements.",
    "Full disclosure is important for claim approval. We have a grace period for minor conditions with medical reports.",
    "I'll explain the key benefits in simple terms and provide a summary sheet for easy understanding.",
    "For pre-existing conditions, we offer coverage after waiting periods. Let me calculate the exact premium.",
    "Let me clarify the current terms and ensure you have accurate information about our policies.",
    "Online policies often have hidden exclusions. Let me show you our comprehensive coverage comparison.",
    "I can offer you our best package with additional benefits at no extra cost if you decide today."
]

async def generate_all_audio_files():
    """Generate audio files for all advisor responses"""
    
    output_dir = "uploads/audio"
    os.makedirs(output_dir, exist_ok=True)
    
    print("🎵 GENERATING AUDIO FILES")
    print("=" * 60)
    print(f"Output directory: {output_dir}")
    print(f"Total responses: {len(ADVISOR_RESPONSES)}")
    print("=" * 60)
    
    for i, text in enumerate(ADVISOR_RESPONSES, 1):
        filename = f"audio_{i:02d}.wav"
        filepath = os.path.join(output_dir, filename)
        
        print(f"\n🎤 Generating {filename}")
        print(f"Text: {text[:60]}...")
        
        try:
            # Generate audio using TTS function directly
            speech_config = speechsdk.SpeechConfig(
                subscription=os.getenv("subscription"),
                region="centralindia"
            )
            speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
            
            synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
            result = synthesizer.speak_text_async(text).get()
            
            if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
                # Save to file
                with open(filepath, 'wb') as f:
                    f.write(result.audio_data)
                
                file_size = len(result.audio_data)
                print(f"✅ Generated: {filename} ({file_size:,} bytes)")
            else:
                print(f"❌ Failed to generate audio for {filename}: {result.reason}")
                
        except Exception as e:
            print(f"❌ Error generating {filename}: {e}")
    
    print(f"\n🎉 AUDIO GENERATION COMPLETE!")
    print(f"📁 Files saved to: {output_dir}")
    print(f"🎵 Generated: audio_01.wav to audio_20.wav")

async def main():
    await generate_all_audio_files()

if __name__ == "__main__":
    asyncio.run(main())