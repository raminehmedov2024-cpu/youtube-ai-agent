import json
import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]


def get_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if creds and not creds.valid and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            creds = None

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file("client_secrets.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("youtube", "v3", credentials=creds)


def upload_video(video_path, title, description, tags,
                 privacy="private", thumbnail=None):
    youtube = get_service()
    body = {
        "snippet": {
            "title": title[:100],
            "description": description,
            "tags": tags,
            "categoryId": "27",
        },
        "status": {
            "privacyStatus": privacy,
            "selfDeclaredMadeForKids": False,
        },
    }
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    request = youtube.videos().insert(
        part="snippet,status", body=body, media_body=media
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Yüklənir: {int(status.progress() * 100)}%")

    video_id = response["id"]

    if thumbnail and os.path.exists(thumbnail):
        try:
            youtube.thumbnails().set(
                videoId=video_id, media_body=MediaFileUpload(thumbnail)
            ).execute()
        except Exception as e:
            print("Örtük şəkli qoyulmadı:", e)

    return video_id


if __name__ == "__main__":
    with open("output/info.json", encoding="utf-8") as f:
        info = json.load(f)

    print("Başlıq:", info["title"])
    print("Video: output/final.mp4")
    answer = input("Private olaraq kanala yüklənsin? (b = bəli, başqa düymə = xeyr): ")

    if answer.strip().lower() == "b":
        vid = upload_video(
            "output/final.mp4",
            info["title"],
            info["description"],
            info["tags"],
            thumbnail="output/thumbnail.jpg",
        )
        print("Yükləndi! Video ID:", vid)
        print("YouTube Studio-da bax: https://studio.youtube.com")
    else:
        print("Yüklənmədi.")