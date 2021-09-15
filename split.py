import os
import sys
from pathlib import Path

if len(sys.argv) <= 1:
  print("split.py FILENAMETOSPLIT.MP3")
  quit()

path = Path(sys.argv[1])
if path.is_file() != True:
  print("Cant find file")
  quit()

try:
  os.mkdir("out")
except:
  print("Dir already exist")
else:
  print("Created out dir")


print("Splitting file %s" % (sys.argv[1]))

# Import the AudioSegment class for processing audio and the 
# split_on_silence function for separating out silent chunks.
from pydub import AudioSegment
from pydub.silence import split_on_silence

# Define a function to normalize a chunk to a target amplitude.
def match_target_amplitude(aChunk, target_dBFS):
    ''' Normalize given audio chunk '''
    change_in_dBFS = target_dBFS - aChunk.dBFS
    return aChunk.apply_gain(change_in_dBFS)

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size

    return trim_ms

# Load your audio.
song = AudioSegment.from_mp3(sys.argv[1])

# Split track where the silence is 2 seconds or more and get chunks using 
# the imported function.
chunks = split_on_silence (
    # Use the loaded audio.
    song, 
    # Specify that a silent chunk must be at least 2 seconds or 2000 ms long.
    min_silence_len = 400,
    # Consider a chunk silent if it's quieter than -16 dBFS.
    # (You may want to adjust this parameter.)
    silence_thresh = -48
)

print("Sliceing chunks")
# Process each chunk with your parameters
for i, chunk in enumerate(chunks):
    # Create a silence chunk that's 0.5 seconds (or 500 ms) long for padding.
    silence_chunk = AudioSegment.silent(duration=500)

    # Add the padding chunk to beginning and end of the entire chunk.
    audio_chunk = silence_chunk + chunk + silence_chunk

    # Normalize the entire chunk.
    normalized_chunk = match_target_amplitude(audio_chunk, -20.0)

    ######Remove silence
    start_trim = detect_leading_silence(normalized_chunk)
    end_trim = detect_leading_silence(normalized_chunk.reverse())
    duration = len(normalized_chunk)
    trimmed_sound = normalized_chunk[start_trim:duration-end_trim]

    # Export the audio chunk with new bitrate.
    print("Exporting chunk{0}.mp3.".format(i))
    trimmed_sound.export(
        ".//out/chunk{0}.mp3".format(i),
        bitrate = "192k",
        format = "mp3"
    )

def detect_leading_silence(sound, silence_threshold=-50.0, chunk_size=10):
    '''
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms
    iterate over chunks until you find the first one with sound
    '''
    trim_ms = 0  # ms
    while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold:
        trim_ms += chunk_size

    return trim_ms
