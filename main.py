import math
import random
import struct
import wave

import note_seq
from note_seq.protobuf import music_pb2

# Adventure scale (C Dorian = heroic vibe)
SCALE = [60, 62, 63, 65, 67, 69, 70]


def next_note(prev: int) -> int:
    """Pick the next melody note with mostly stepwise movement."""
    step = random.choice([-2, -1, 1, 2])
    candidate = prev + step
    return min(SCALE, key=lambda pitch: abs(pitch - candidate))


def generate_sequence(length: int = 80) -> music_pb2.NoteSequence:
    """Generate a layered orchestral-style NoteSequence."""
    sequence = music_pb2.NoteSequence()
    sequence.tempos.add(qpm=110)

    strings_program = 48
    brass_program = 56
    bass_program = 33

    current_pitch = random.choice(SCALE)
    time = 0.0

    for i in range(length):
        if i < 20:
            durations = [0.5, 1.0]
        elif i < 50:
            durations = [0.25, 0.5]
        else:
            durations = [0.25]

        duration = random.choice(durations)

        melody = sequence.notes.add()
        melody.pitch = current_pitch
        melody.start_time = time
        melody.end_time = time + duration
        melody.velocity = random.randint(70, 100)
        melody.instrument = 0
        melody.program = strings_program

        if i % 2 == 0:
            bass = sequence.notes.add()
            bass.pitch = current_pitch - 12
            bass.start_time = time
            bass.end_time = time + duration * 2
            bass.velocity = 60
            bass.instrument = 1
            bass.program = bass_program

        if i > 50 and i % 4 == 0:
            brass = sequence.notes.add()
            brass.pitch = current_pitch + 12
            brass.start_time = time
            brass.end_time = time + duration
            brass.velocity = 110
            brass.instrument = 2
            brass.program = brass_program

        current_pitch = next_note(current_pitch)
        time += duration

    sequence.total_time = time
    return sequence


def save_midi(sequence: music_pb2.NoteSequence, filename: str = "ai_output.mid") -> None:
    note_seq.sequence_proto_to_midi_file(sequence, filename)
    print(f"Generated MIDI: {filename}")


def _midi_to_frequency(pitch: int) -> float:
    return 440.0 * (2.0 ** ((pitch - 69) / 12.0))


def save_wav(
    sequence: music_pb2.NoteSequence,
    filename: str = "ai_output.wav",
    sample_rate: int = 44100,
) -> None:
    """Render NoteSequence to a simple synthesized WAV file (mono)."""
    total_time = max((note.end_time for note in sequence.notes), default=0)
    num_samples = max(1, int(total_time * sample_rate) + 1)
    audio = [0.0] * num_samples

    for note in sequence.notes:
        start_idx = int(note.start_time * sample_rate)
        end_idx = min(num_samples, int(note.end_time * sample_rate))
        if end_idx <= start_idx:
            continue

        frequency = _midi_to_frequency(note.pitch)
        amplitude = (note.velocity / 127.0) * 0.18

        for idx in range(start_idx, end_idx):
            t = idx / sample_rate
            sample = math.sin(2 * math.pi * frequency * t)

            # Short release fade to reduce clicks.
            tail = end_idx - idx
            if tail < int(0.01 * sample_rate):
                sample *= tail / max(1, int(0.01 * sample_rate))

            audio[idx] += sample * amplitude

    peak = max(max(audio), -min(audio), 1e-9)
    normalization = min(0.95 / peak, 1.0)

    with wave.open(filename, "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)

        frames = bytearray()
        for sample in audio:
            value = int(max(-1.0, min(1.0, sample * normalization)) * 32767)
            frames.extend(struct.pack("<h", value))

        wav_file.writeframes(frames)

    print(f"Generated WAV: {filename}")


if __name__ == "__main__":
    seq = generate_sequence()
    save_midi(seq)
    save_wav(seq)
