from dotenv import load_dotenv
import asyncio

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.plugins import (
    google,
    noise_cancellation,
)
import os
import requests
import time

load_dotenv()


GLADIA_API_KEY = os.getenv("GLADIA_API_KEY")
endpoint = "https://api.assemblyai.com/v2/transcript"

last_youtube_participant = None

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful youtube video explinaer in malayalam language")


_active_tasks = set()
latest_youtube_links = {}

def transcribe_youtube_video(youtube_url):
    endpoint = "https://api.gladia.io/v2/transcription/"
    headers = {
        "x-gladia-key": GLADIA_API_KEY,
        "Content-Type": "application/json"
    }
    payload = {
        "video_url": youtube_url,
        "diarization": False,
        "subtitles": False
    }
    resp = requests.post(endpoint, headers=headers, json=payload)
    resp.raise_for_status()
    body = resp.json()
    result_url = body.get("result_url")
    if not result_url:
        raise Exception("No result_url returned")
    while True:
        r = requests.get(result_url, headers=headers)
        r.raise_for_status()
        data = r.json()
        if data.get("status") == "done":
            return data["result"]["transcription"]["full_transcript"]
        elif data.get("status") == "error":
            raise Exception("Transcription error: " + str(data))
        time.sleep(2)

async def async_handle_youtube_link(reader, participant_identity, session):
    link = await reader.read_all()
    global last_youtube_participant
    latest_youtube_links[participant_identity] = link
    last_youtube_participant = participant_identity
    print(f"Received YouTube link from {participant_identity}: {link}")
    try:
        await session.generate_reply(
            instructions="my video is processing so we can make some fun chat until it done"
        )
        loop = asyncio.get_event_loop()
        transcript_text = await loop.run_in_executor(
            None, transcribe_youtube_video, link
        )
        print(transcript_text)
        # This message will be sent as soon as the transcript is ready,
        # regardless of what the user said in between.
        instructions = f"Use this transcript: {transcript_text}"
        session.llm.instructions = instructions
        await session.generate_reply(instructions=f"video details ready reply based on this video:{transcript_text}, ask me questions!")
    except Exception as e:
        print(f"Transcription failed: {e}")
        await session.generate_reply(
            instructions="Sorry, I couldn't process this YouTube link. Please provide a direct video or audio link."
        )
#setup
def handle_youtube_link(reader, participant_identity,session):
    task = asyncio.create_task(async_handle_youtube_link(reader, participant_identity,session))
    _active_tasks.add(task)
    task.add_done_callback(lambda t: _active_tasks.remove(t))
    
    
async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
    llm=google.beta.realtime.RealtimeModel(
        model="gemini-2.0-flash-exp",
        voice="Puck",
        temperature=0.8,
        instructions="You are a helpful youtube video explinaer in malayalam language",
    ),
    )
    ctx.room.register_text_stream_handler("youtube-link",lambda reader, participant_identity: handle_youtube_link(reader, participant_identity, session))
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )
    await ctx.connect()
    global latest_youtube_links
    global last_youtube_participant
    if (
        last_youtube_participant is not None and
        last_youtube_participant in latest_youtube_links and
        len(latest_youtube_links[last_youtube_participant]) > 0
        ):
        await session.generate_reply(
            instructions="thank"
        )
    else:
        await session.generate_reply(
            instructions="Greet frist in malayalam language then ask user to enter the link of video so i can assit "
        )   


if __name__ == "__main__":
    import time
    while True:
        try:
            print("Starting LiveKit YouTube Agent...")
            agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
        except Exception as e:
            print(f"Worker stopped: {e}")
        print("Retrying in 5 seconds...")
        time.sleep(5)

