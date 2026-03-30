import random
import note_seq
from note_seq.protobuf import music_pb2

# --- "AI" via Markov transitions ---
# Each note tends to follow certain others

transition_map = {
    60: [60, 62, 64, 65],
    62: [60, 62, 64, 67],
    64: [62, 64, 65, 67],
    65: [64, 65, 67, 69],
    67: [65, 67, 69, 71],
    69: [67, 69, 71],
    71: [69, 71, 72],
    72: [71, 72]
}

def generate_sequence(length=32):
    sequence = music_pb2.NoteSequence()
    sequence.tempos.add(qpm=120)

    current_pitch = random.choice(list(transition_map.keys()))
    time = 0.0

    for _ in range(length):
        duration = random.choice([0.25, 0.5, 1.0])

        note = sequence.notes.add()
        note.pitch = current_pitch
        note.start_time = time
        note.end_time = time + duration
        note.velocity = 80

        # Choose next note based on transitions
        current_pitch = random.choice(transition_map.get(current_pitch, [60]))
        time += duration

    return sequence

def save_midi(sequence, filename="ai_output.mid"):
    note_seq.sequence_proto_to_midi_file(sequence, filename)
    print(f"✅ Generated: {filename}")

if __name__ == "__main__":
    seq = generate_sequence()
    save_midi(seq)
    input("Press Enter to exit...")
