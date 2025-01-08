from mido import MidiFile

#This module is for determining all the unique notes that are played in the song, and returns them as a dictionary.
#All code by Heinz Sander


def get_note_spread(midifile):
    mid = MidiFile(midifile, clip=True)
    output_dict = {}
    for track in mid.tracks:
        if len([message for message in track if message.type == "note_on"]) == 0:
            continue
        #print(track.name)
        note_dict = {}
        for message in track:
            if message.type == "note_on":
                if not message.note in note_dict.keys():
                    note_dict[message.note] = 1
                else:
                    note_dict[message.note] += 1
        #print(note_dict)
        output_dict[track.name] = note_dict
    #print(output_dict)
    return output_dict

def convert_to_note_name(note_num):
    note_list = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
    note_index = (note_num % 12)
    note_num -= 21
    octave = int(((note_num - 3) / 12))
    note_string = f"{note_list[note_index]}{octave}"
    return note_string

def print_track_list(midifile):
    mid = MidiFile(midifile, clip=True)
    print("TRACK INDICES:")
    for i in range(len(mid.tracks)):
        track = mid.tracks[i]
        print(f"{i}) {track.name}")

def pretty_output(note_spread):
    for track in note_spread.keys():
        print(f"{track}:")
        note_keys = list(note_spread[track].keys())
        note_keys.sort()
        for i in range(len(note_keys)):
            note_key = note_keys[i]
            print(f"{i+1}| {note_key} ({convert_to_note_name(note_key)}): played {note_spread[track][note_key]} times")
        print(f"Total number of different notes: {len(note_keys)}")
        print()

if __name__ == "__main__":
    midifile = "/home/heinz/Blender/AniMIDI/Axel F/Music/axel_f_04.mid"
    print_track_list(midifile)
    print()
    note_spread = get_note_spread(midifile)
    pretty_output(note_spread)
