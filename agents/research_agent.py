import os

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
	api_key=os.getenv("OPENAI_API_KEY")
)


def research_topic(topic):
	prompt = f"""
You are a professional YouTube research agent.

Our YouTube channel is about:
AI, technology and the future.

Research topic:
{topic}

Your job is to analyze this topic and provide:

1. Why people might care about this topic
2. What makes the topic interesting
3. 5 possible video angles
4. Possible risks or problems with the topic
5. A recommended YouTube video title
6. A short explanation of the recommended angle

Do not copy other creators.
Create original angles.
"""

	response = client.responses.create(
		model="gpt-5.6",
		input=prompt
	)

	return response.output_text
