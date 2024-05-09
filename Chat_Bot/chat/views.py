import json
import os
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from gpt import models 
from import ChatHistory # type: ignore
from gpt.serializers import ChatHistorySerializer # type: ignore
from openai import OpenAI
from pydub import AudioSegment
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# Define the starting prompt
STARTING_PROMPT = "TYPE YOUR PROJECT DETAILS BASED TO TRAIN GPT"

class ChatBotView(APIView):
    def post(self, request, user_id=None):
        # Extract necessary data from the request
        chat_type = request.data.get('chat_type', None)
        user = request.data.get('user_id', None)
        text = request.data.get('user_chat', None)
        audio_file = request.data.get('audio', None)

        # Perform actions based on the chat type
        if chat_type == 'text':
            return self.handle_text_chat(request)
        elif chat_type == 'audio':
            return self.handle_audio_chat(request)
        else:
            return Response({"error": "Invalid chat type"}, status=400)

    def get(self, request, user_id):
        # Retrieve chat history for a specific user
        chat_history = ChatHistory.objects.filter(user_id__id=user_id)
        serializer = ChatHistorySerializer(chat_history, many=True)
        return Response(serializer.data)

    def delete(self, request, user_id):
        # Delete chat history for a specific user
        ChatHistory.objects.filter(user_id__id=user_id).delete()
        return Response({})

    def handle_text_chat(self, request):
        # Serialize and save chat history for text chat
        serializer = ChatHistorySerializer(data=request.data)
        return self.serializer_valid_check(serializer, request.data)

    def handle_audio_chat(self, request):
        # Convert audio to text, save chat history, translate, and save translation for audio chat
        chat_history = self.audio_conversion(request)
        if isinstance(chat_history, Response):
            return chat_history
        
        client = OpenAI(api_key="YOUR_API_KEY")
        audio_file = open(chat_history.audio.path, "rb")
        transcript = client.audio.transcriptions.create(model="whisper-1", file=audio_file)
        text = transcript.text
        chat_history.user_chat = text
        chat_history.save()
        chat_historys = ChatHistory.objects.filter(user_id__id=user)
        messages = self.chat_text(chat_historys, STARTING_PROMPT)
        translation = self.transilated_data(client, messages)
        if isinstance(translation, Response):
            return translation
        chat_history.response_chat = translation
        chat_history.save()
        serializer = ChatHistorySerializer(instance=chat_history)
        return Response(serializer.data, status=200)

    def chat_text(self, chat_historys, starting_prompt):
        # Prepare chat history messages for display
        messages = [{"role": "system", "content": starting_prompt}]
        for chat_history in chat_historys:
            if chat_history.user_chat:
                messages.append({"role": "user", "content": f"user_chat = {chat_history.user_chat}"})
            if chat_history.response_chat:
                messages.append({"role": "system", "content": chat_history.response_chat})
        return messages

    def serializer_valid_check(self, serializer, data):
        # Check if the serializer is valid and return the instance or errors
        if serializer.is_valid():
            return serializer.save()
        else:
            return Response(serializer.errors, status=400)

    def transilated_data(self, client, messages):
        # Translate chat history messages
        try:
            response = client.chat.completions.create(model="gpt-4-1106-preview", response_format={"type": "json_object"}, messages=messages)
            message = response.choices[0].message.content
            data = json.loads(message)
            translation = data.get("data", None)
            return translation
        except Exception as e:
            return Response(str(e))

    def audio_conversion(self, request):
        # Convert audio files to MP3 format and save
        audio_file = request.data.get('audio', None)
        user = request.data.get('user_id', None)
        chat_type = request.data.get('chat_type', None)
        if chat_type =='audio':
            try:
                audio_content = audio_file.read()
                audio_segment = AudioSegment.from_file(io.BytesIO(audio_content), frame_rate=44100, channels=2, sample_width=2)
                modified_audio_content = audio_segment.export(format="mp3").read()
                file_name = audio_file._name
                modified_audio_file = ContentFile(modified_audio_content, name=f'{file_name}.mp3')
                data = request.data.copy()
                data['audio'] = modified_audio_file
                serializer = ChatHistorySerializer(data=data)
                if serializer.is_valid():
                    chat_history = serializer.save()
                    modified_audio_content = None
                    return chat_history
            except Exception as E:
                return Response(str(E), status=400)
        return Response({"error": "No audio file found"}, status=400)
