import random
import note_seq
from note_seq.protobuf import music_pb2

# --- Adventure scale (Dorian = heroic vibe) ---
scale = [60, 62, 63, 65, 67, 69, 70]  # C D Eb F G A Bb

def next_note(prev):
    # Move mostly stepwise (smooth melody)
    step = random.choice([-2, -1, 1, 2])
    new = prev + step

    # Snap to nearest scale note
    return min(scale, key=lambda x: abs(x - new))

def generate_sequence(length=80):
    sequence = music_pb2.NoteSequence()
    sequence.tempos.add(qpm=110)

    current_pitch = random.choice(scale)
    time = 0.0

    for i in range(length):
        # Build energy over time
        if i < 20:
            durations = [0.5, 1.0]      # slow intro
        elif i < 50:
            durations = [0.25, 0.5]     # movement
        else:
            durations = [0.25]          # fast climax

        duration = random.choice(durations)

        # --- Melody ---
        note = sequence.notes.add()
        note.pitch = current_pitch
        note.start_time = time
        note.end_time = time + duration
        note.velocity = random.randint(70, 100)

        # --- Bass (every 2 beats) ---
        if i % 2 == 0:
            bass = sequence.notes.add()
            bass.pitch = current_pitch - 12
            bass.start_time = time
            bass.end_time = time + duration * 2
            bass.velocity = 60

        # Move to next note
        current_pitch = next_note(current_pitch)
        time += duration

    return sequence

def save_midi(sequence, filename="ai_output.mid"):
    note_seq.sequence_proto_to_midi_file(sequence, filename)
    print(f"Generated: {filename}")

if __name__ == "__main__":
    seq = generate_sequence()
    save_midi(seq)
    input("Press Enter to exit...")
