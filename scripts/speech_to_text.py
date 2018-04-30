import io


def transcribe_file(audio_file):
    """Transcribe the given audio file."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    # [START migration_sync_request]
    # [START migration_audio_config_file]
    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US')
    # [END migration_audio_config_file]

    # [START migration_sync_response]
    response = client.recognize(config, audio)
    # [END migration_sync_request]
    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    for result in response.results:
        # The first alternative is the most likely one for this portion.
        return result.alternatives[0].transcript


# [END migration_sync_response]


if __name__ == '__main__':
    speech_file = "audio.raw"
    with io.open(speech_file, 'rb') as audio_file:
        audio_content = audio_file.read()
    print(transcribe_file(audio_content))
