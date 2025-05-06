from fastapi import APIRouter, Depends, HTTPException,UploadFile,Form,File,Response, status, Body, Path, Query
import azure.cognitiveservices.speech as speechsdk
import tempfile
import os
import time
from pydantic import BaseModel
from typing import List
import aiofiles
import asyncio
from dotenv import load_dotenv

load_dotenv(".env")
import datetime
subscription =  os.getenv("subscription")

router = APIRouter(prefix="/speech", tags=["speech"])

class SpeechRecognitionResponse(BaseModel):
    text: str
    status: str
    

speech_config = speechsdk.SpeechConfig(  
        subscription=subscription,  
        region="centralindia",  
    )
speech_config_ = speechsdk.SpeechConfig(  
        subscription=subscription,  
        region="centralindia",  
    )    
@router.post("/stt", response_model=SpeechRecognitionResponse)  
async def speech_recognition_endpoint(file: UploadFile = File(...), language_code: str = Form(...)):  
    """  
    FastAPI endpoint that accepts an audio file via POST request and  
    performs continuous speech recognition using Azure Speech SDK.  
    """ 
    print(file) 
    # Check file type (optional)  
    if not file.content_type.startswith("audio/"):  
        raise HTTPException(status_code=400, detail="File must be an audio file")  
  
    # Unfortunately, the Speech SDK requires a file on disk  
    # We need to temporarily save the file  
    async with aiofiles.tempfile.NamedTemporaryFile(delete=False) as temp_file:  
        temp_file_name = temp_file.name  
  
    try:  
        # Write uploaded file content to temporary file  
        async with aiofiles.open(temp_file_name, "wb") as buffer:  
            content = await file.read()  
            await buffer.write(content)  
  
        # Call the continuous speech recognition function  
        recognized_text = await stt(temp_file_name, language_code)  
  
        return SpeechRecognitionResponse(  
            text=recognized_text,  
            status="success"  
        )  
    finally:  
        # Clean up the temporary file  
        if os.path.exists(temp_file_name):  
            os.unlink(temp_file_name)  
  
async def stt(filename, language):  
    """  
    Continuous speech recognition function that processes an audio file  
    and returns the recognized text.  
    """  
    result_text = []  
  

    speech_config.set_profanity(speechsdk.ProfanityOption.Raw)
    speech_config.speech_recognition_language = language 
  
    audio_config = speechsdk.audio.AudioConfig(filename=filename)  
    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)  
  
    done = asyncio.Event()  
  
    def stop_cb(evt: speechsdk.SessionEventArgs):  
        """callback that signals to stop continuous recognition upon receiving an event `evt`"""  
        done.set()  
  
    # Connect callbacks to the events fired by the speech recognizer  
    speech_recognizer.recognized.connect(lambda evt: result_text.append(evt.result.text))  
    # Stop continuous recognition on either session stopped or canceled events  
    speech_recognizer.session_stopped.connect(stop_cb)  
    speech_recognizer.canceled.connect(stop_cb)  
  
    # Start continuous speech recognition  
    speech_recognizer.start_continuous_recognition_async()  
  
    # Wait until recognition is done  
    await done.wait()  
  
    speech_recognizer.stop_continuous_recognition_async()  
  
    text = " ".join(result_text)  
    print("YOU: ", text)  
    return text 



@router.post("/tts")
async def text_to_speech(
    message: str = Form(...),
    voice_id: str = Form(default="ar-SA-HamedNeural"),
):

    speech_config_.speech_synthesis_voice_name = voice_id
    print(voice_id)
    # Use default speaker output but capture the result
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config_, audio_config=None)
    start=datetime.datetime.now()
    print(start)
    result = synthesizer.speak_text_async(message).get()
    print(datetime.datetime.now()-start)
    print(result)
    # if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    return Response(
            content=result.audio_data,
            media_type="audio/wav",
            headers={"Content-Disposition": "attachment; filename=speech.wav"}
        )
    # else:
    #     return Response(
    #         content=f"Speech synthesis failed: {result.cancellation_details}",
    #         status_code=500
    #     )
