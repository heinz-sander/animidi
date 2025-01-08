# AniMIDI by Heinz Sander, a set of tools for making Python scripts for making music animations with Blender.

# Examples for frequently-used functions:

# Inserting timeline markers is usefull for debugging
# scene.timeline_markers.new('F_01', frame=1)

# Inserting keyframes is the entire point of this library.
'''
animidi.insert_keyframe(
    target_object = None,
    data_path = None,
    index = None,
    frame = None,
    value = None,
    handle_left_type = None,
    handle_left = None,
    handle_right_type = None,
    handle_right = None,
    interpolation = None,
    exclude_func = None
)

'''

# Exclude functions: touch it if True, don't touch it if False
# insert/delete keyframes there if True, don't do it if False
# okay if True, not okay if False

# Import stuff
if __name__ != "__main__":
    import bpy

import copy

try:
    from mido import MidiFile
except ImportError:
    print("This module depends on Mido for MIDI support. Please make sure you have this module installed.")

print("AniMIDI has been successfully imported.")

# This function gets the current value of the data_path of the target_object at frame_num. This function is hardly usefull at all.
def get_current_value(frame_num, target_object, data_path, index=None):
    bpy.context.scene.frame_set(frame_num)
    if index == None:
        return eval(f"target_object.{data_path}")
    else:
        return eval(f"target_object.{data_path}[{index}]")

# This is the real meat and potatoes of AniMIDI.
# This function inserts a keyframe on data_path[index, if applicable] of target_object at frame.
# You can optionally set the handles and the interpolation, too.
# exclude_func should return True if it's OK to insert the keyframe, and False if it's not.
def insert_keyframe(target_object=None, data_path=None, index=None, frame=None, value=None, handle_left=None, handle_left_type=None, handle_right=None, handle_right_type=None, interpolation=None, argh=None, exclude_func=None):
    # The handle_left and handle_right take lists of the handle offsets from the keyframe's position

    if callable(exclude_func):
        if exclude_func(frame) == False: # if it's False, don't insert the keyframe
            return None

    if target_object is None: raise ValueError
    if data_path is None: raise ValueError
    if frame is None: raise ValueError
    if value is None: raise ValueError

    # find fcurve
    if target_object.animation_data is None:
        target_object.animation_data_create()
    animation_data = target_object.animation_data

    if animation_data.action is None:
        animation_data.action = bpy.data.actions.new("anim_data")

    if index == None:
        fc = animation_data.action.fcurves.find(data_path)
        if fc is None:
            fc = animation_data.action.fcurves.new(data_path)
    else:
        fc = animation_data.action.fcurves.find(data_path, index=index)
        if fc is None:
            fc = animation_data.action.fcurves.new(data_path, index=index)
    if value == "current":
        new_frame = fc.keyframe_points.insert(frame, value=get_current_value(target_object, data_path, index))
    else:
        new_frame = fc.keyframe_points.insert(frame, value)

    if handle_left_type is not None:
        new_frame.handle_left_type = handle_left_type
    if handle_right_type is not None:
        new_frame.handle_right_type = handle_right_type

    if handle_left is not None:
        if len(handle_left) != 2:
            raise ValueError("handle_left requires a list of numbers of exactly length 2")
        new_frame.handle_left = (new_frame.co[0] + handle_left[0], new_frame.co[1] + handle_left[1])

    if handle_right is not None:
        if len(handle_right) != 2:
            raise ValueError("handle_right requires a list of numbers of exactly length 2")
        new_frame.handle_right = (new_frame.co[0] + handle_right[0], new_frame.co[1] + handle_right[1])

    if interpolation is not None:
        new_frame.interpolation = interpolation

    return new_frame

# This function acts just the same as insert_keyframe, but handles x, y, and z values all at the same time.
# values should be a list of three numbers, describing the x, y, and z (in that order) location or rotation values.
# handle_positions should be a list of three lists (one for X, Y, and Z) each containing two lists (one for handle_left and one for handle_right) each containing two numbers (relative offset of X and Y, respectively). Any one of these can be None.
def insert_multi_keyframe(target_object=None, data_path=None, frame=None, values=None, handle_left_type=None, handle_right_type=None, handle_positions=None, interpolation=None, exclude_func=None):
    if not isinstance(values, list):
        raise ValueError("Values must be a list of length 3")
    if not len(values) == 3:
        raise ValueError("Values must have a length of 3")

    if handle_positions is None:
        handle_positions = [None, None, None]
    else:
        if type(handle_positions) is not list or len(handle_positions) != 3:
            raise ValueError

    for i in range(3):
        if handle_positions[i] is None:
            handle_left = None
            handle_right = None
        else:
            handle_left_type = "FREE"
            handle_right_type = "FREE"
            handle_left = handle_positions[i][0]
            if handle_left is not None:
                if type(handle_left) is not list or len(handle_left) != 2:
                    raise ValueError

            handle_right = handle_positions[i][1]
            if handle_right is not None:
                if type(handle_right) is not list or len(handle_right) != 2:
                    raise ValueError

        insert_keyframe(
            target_object = target_object,
            data_path = data_path,
            index = i,
            frame = frame,
            value = values[i],
            handle_left_type = handle_left_type,
            handle_left = handle_left,
            handle_right_type = handle_right_type,
            handle_right = handle_right,
            interpolation = interpolation,
            argh = "MONEY",
            exclude_func = exclude_func
        )

# This function acts just like insert_keyframe, but inserts x, y, and z position and rotation values for the target_object based on the position of position_object.
def insert_position_keyframe(target_object, frame, position_object, handle_left_type=None, handle_right_type=None, handle_positions=None, interpolation=None, exclude_func=None):

    if handle_positions is None:
        handle_positions = [[None, None, None], [None, None, None]]
    else:
        if type(handle_positions) is not list or len(handle_positions) != 2:
            raise ValueError

    object_loc = list(position_object.location)
    insert_multi_keyframe(
        target_object = target_object,
        data_path = "location",
        frame = frame,
        values = object_loc,
        handle_left_type = handle_left_type,
        handle_right_type = handle_right_type,
        handle_positions = handle_positions[0],
        interpolation = interpolation,
        exclude_func = exclude_func
    )

    object_rot = list(position_object.rotation_euler)
    insert_multi_keyframe(
        target_object = target_object,
        data_path = "rotation_euler",
        frame = frame,
        values = object_rot,
        handle_left_type = handle_left_type,
        handle_right_type = handle_right_type,
        handle_positions = handle_positions[1],
        interpolation = interpolation,
        exclude_func = exclude_func
    )

# Base class for AniMIDI notes.
# note-on and note-off messages are bundled into one note.
class Note():
    def __init__(self, noteon_time, noteoff_time, channel, note, velocity, id):
        self.is_animidi = True
        self.note_on = noteon_time
        self.note_off = noteoff_time
        self.note_val = note
        self.velocity = velocity
        self.channel = channel
        self.id = id

    def __str__(self):
        return f"AniMIDI note object;\nid = {self.id}\nnote on = {self.note_on}\nnote off = {self.note_off}\nnote value = {self.note_val}\nvelocity = {self.velocity}\nchannel = {self.channel}"

# Functions for loading messages:

def messages_to_tick_time(track_list):
    # This works because all messages in the track are in the order in which they occur,
    # and each message's time is the delta time to the last message.
    prev_time = 0
    for message in track_list:
        message.time = message.time + prev_time
        prev_time = message.time
    return track_list

# This currently only supports discrete (not sliding) tempo changes
def messages_to_abs_time(track_list, tpb):
    current_tempo = get_first_tempo(track_list)
    last_tempo = current_tempo
    ticks_per_beat = tpb
    offset = 0
    last_tempo_change_time = 0
    last_tempo_change_tick = 0
    for message in track_list:
        if message.type == "set_tempo":
            last_tempo = current_tempo
            current_tempo = message.tempo
            duration_of_last_segment = (abs(message.time - last_tempo_change_tick) / tpb) * (last_tempo / 1000000)
            time_of_this_tempo_change = last_tempo_change_time + duration_of_last_segment
            last_tempo_change_time = time_of_this_tempo_change
            last_tempo_change_tick = message.time
            time_where_it_would_be = ((message.time / tpb) * (current_tempo / 1000000))
            offset = time_of_this_tempo_change - time_where_it_would_be

        # convert to beats
        message.time = message.time / tpb
        # convert to seconds
        message.time = (message.time * (current_tempo / 1000000)) + offset
    return track_list

def get_first_tempo(track):
    for message in track:
        if message.type == "set_tempo":
            return message.tempo
    return 600000

def messages_to_frame_time(track_list, fps, offset):
    for message in track_list:
        message.time = (message.time * fps) + offset
    return track_list

def messages_to_note_objs(track_list):
    def get_matching_noteoff(noteon_msg):
        for message in track_list:
            if message.type == "note_off":
                if message.note == noteon_msg.note:
                    if message.channel == noteon_msg.channel:
                        #if message.velocity == noteon_msg.velocity:
                        #note_off messages don't necessarily have the same velocity
                        return track_list.pop(track_list.index(message))

    #noteon_msg = None
    #noteoff_msg = None
    output = []
    i = 0
    while 1:
        try:
            first_msg = track_list.pop(0)
        except IndexError:
            return output

        if not first_msg.type == "note_on" or first_msg.type == "note_off":
            continue

        if first_msg.type == "note_on":
            # if the type is note_on, iterate through the list until you find a matching note_off,
            # pop it, and combine the two into a note object
            noteon_msg = first_msg
            noteoff_msg = get_matching_noteoff(noteon_msg)
            if noteoff_msg is None:
                raise Exception("Something is wrong here -- unmatched note-on message")
            new_note_obj = Note(
                noteon_time = noteon_msg.time,
                noteoff_time = noteoff_msg.time,
                channel = noteon_msg.channel,
                note = noteon_msg.note,
                velocity = noteon_msg.velocity,
                id = i
            )
            i += 1
            output.append(new_note_obj)

    return output

def combine_message_tracks(track_1, track_2):
    track1 = copy.deepcopy(track_1)
    track2 = copy.deepcopy(track_2)
    track1 += track2
    return sorted(track1, key=lambda msg: msg.time)

def combine_note_tracks(track_1, track_2):
    track1 = copy.deepcopy(track_1)
    track2 = copy.deepcopy(track_2)
    track1 += track2
    return sorted(track1, key=lambda note: note.note_on)

# This function converts the specified track into a list of note objects.
# fps should be the frames per second of your animation.
# offset is by number of frames, in case you want fine control of the offset between different tracks.
def load_track(midifile, track_index, fps, offset, tc_track_index=0):
    mid = MidiFile(midifile, clip=True)
    raw_track = list(mid.tracks[track_index])
    tick_time_track = messages_to_tick_time(raw_track)

    tempo_change_track = list(mid.tracks[tc_track_index])
    tick_time_tc_track = messages_to_tick_time(tempo_change_track)

    # add tempo change messages to the track
    whole_track = combine_message_tracks(tick_time_track, tick_time_tc_track)

    ticks_per_beat = mid.ticks_per_beat
    abs_time_track = messages_to_abs_time(whole_track, ticks_per_beat)

    frame_time_track = messages_to_frame_time(abs_time_track, fps, offset)

    finished_track = messages_to_note_objs(frame_time_track)
    return finished_track

# This function gets the next note (or previous note) to a given note in a track. Returns None if it was the last (or first, if previous) note.
def get_next_note(track, note, direction, match_note=False, val_function=None):
    # Argument validation
    if direction != "next" and direction != "previous":
        raise ValueError("Direction must be \"next\" or \"previous\"")

    if not isinstance(match_note, bool):
        raise ValueError("match_note must be True or False")

    if val_function is not None:
        if not callable(val_function):
            raise ValueError("val_function must be a callable function")

    if note not in track:
        raise IndexError("That note isn't in that track. Maybe you have the wrong track?")

    # Main Block
    if direction == "next":
        track_range = range(track.index(note) + 1, len(track))
    else:
        if track.index(note) <= 0:
            return None
        else:
            track_range = range(track.index(note) - 1, -1, -1)

    for x in track_range:
        x_note = track[x]
        if match_note:
            if x_note.note_val == note.note_val:
                l_note = x_note
            else:
                continue
        else:
            l_note = x_note

        if val_function is not None:
            if val_function(l_note):
                return l_note
            else:
                continue
        else:
            return l_note
    return None

# This function is usefull for scaling based on maximum and minimum values.
# x1 and x2 cover the input range.
# y1 and y2 determine the output range.
# optional max and min can be used to cap the output.
def scale_linear(val, x1, x2, y1, y2, max=None, min=None):
    result = (((y2 - y1) / (x2 - x1)) * (val - x1)) + y1
    if max is not None:
        if not isinstance(max, (float, int)):
            raise ValueError("max must be a number")
        if result > max:
            return max
    if min is not None:
        if not isinstance(min, (float, int)):
            raise ValueError("min must be a number")
        if result < min:
            return min
    return result

# SIMPLE AND BORING

# Function to remove all the keyframes from a Blender object.
# exclude_func should return True if it's OK to remove the keyframe, and False if it's not.
def remove_object_keyframes(object, exclude_func=None):
    if exclude_func is not None:
        if not callable(exclude_func):
            raise ValueError("exclude_func must be a callable function")

    if object.animation_data is None:
        return None

    if object.animation_data.action is None:
        return None

    for fcurve in object.animation_data.action.fcurves:
        remove_fcurve_keyframes(fcurve, exclude_func)

def remove_fcurve_keyframes(fcurve, exclude_func=None):
    i = 0
    while i < len(fcurve.keyframe_points):
        keyframe = fcurve.keyframe_points[i]
        if exclude_func == None:
            fcurve.keyframe_points.remove(keyframe)
        else:
            if exclude_func(keyframe.co.x) == True: # if exclude_func is True, remove the keyframe
                fcurve.keyframe_points.remove(keyframe)
            else:
                i += 1


class MetaObject:
    def __init__(self, bl_obj, bl_material, midi_note):
        self.bl_obj = bl_obj
        # If no material was supplied, just use the object's active material, because if the object has more than one material slot, I have no idea which slot to use by default.
        if bl_material is None:
            self.bl_material = bl_obj.active_material
        else:
            self.bl_material = bl_material
        self.midi_note = midi_note

    def __str__(self):
        return f"Animidi ObjectManager MetaObject: bl_obj = {self.bl_obj}; bl_material = {self.bl_material}; midi_note = {self.midi_note}"

# This class is tricky to use. You must have a set of objects allready made, and they must be unlinked from each other.
# The objects must be called "[obj_set_name].001", "[obj_set_name].002", etc.
# And, if assign_individual_materials is True, the first object ([obj_set_name].001) must have a material named "[obj_set_name]_material.001".
# (All other members of the set will recieve independent copies of this material.)
# midi_notes must be a dictionary with the keys being the numbers of the objects (1, 2, 3, etc) and the values being the MIDI note numbers assigned to those objects.
# (I could have used a simple list, but this way is more reader-friendly ;)
# You can get an object like this: object_manager[00x number]
# Or you can get it with its midi note number with the get_obj_by_midi_note() function.
# IMPORTANT!
# If remove_keyframes is False, the first material won't be copied to the other ones
# (because doing so would remove their keyframes).
# This means assign_individual_materials and remove_keyframes are mutually exclusive.
# Furthermore, both of them have to be set to True in order for the copying to happen.
class ObjectManager:
    def __init__(self, obj_set_name, obj_set_size, midi_notes, assign_individual_materials = False, remove_keyframes = False, remove_material_keyframes = None, exclude_func = None):
        if not isinstance(obj_set_name, str):
            raise ValueError("obj_set_name must be a string")

        if not isinstance(obj_set_size, int):
            raise ValueError("obj_set_size must be an integer")

        if midi_notes is not None:
            if not isinstance(midi_notes, dict):
                raise ValueErrror("midi_notes must be a dictionary")

            for key, val in midi_notes.items():
                if not isinstance(key, int) or not isinstance(val, int):
                    raise ValueError("midi_notes dictionary must contain valid indices and MIDI note numbers. Read the comments in animidi.py.")

        if not isinstance(assign_individual_materials, bool):
            raise ValueError("assign_individual_materials must be True or False")

        if not isinstance(remove_keyframes, bool):
            raise ValueError("remove_keyframes must be True or False")

        if remove_material_keyframes is None:
            remove_material_keyframes = remove_keyframes
        else:
            if not isinstance(remove_material_keyframes, bool):
                raise ValueError("remove_material_keyframes must be True or False")

        # Loop through all materials and delete the unused ones for the object set
        if assign_individual_materials:
            # Don't delete them if remove_material_keyframes is False
            if not remove_material_keyframes:
                for material in bpy.data.materials:
                    if material.name[0:(len(obj_set_name) + len("_material"))] == f"{obj_set_name}_material":
                        # Don't delete the first material!
                        if material.name != f"{obj_set_name}_material.001":
                            bpy.data.materials.remove(material, do_unlink=True)


        self.object_list = []
        obj_001 = bpy.data.objects[f"{obj_set_name}.001"]
        if assign_individual_materials:
            obj_material_001 = bpy.data.materials[f"{obj_set_name}_material.001"]

        for i in range(1, obj_set_size + 1):
            bl_obj = bpy.data.objects[f"{obj_set_name}.{i:03d}"]
            if remove_keyframes:
                remove_object_keyframes(bl_obj, exclude_func = exclude_func)
                # remove keyframes from obj's active material (might cause problems on objects with more than one material)
                if remove_material_keyframes:
                    if bl_obj.active_material is not None:
                        remove_object_keyframes(bl_obj.active_material, exclude_func = exclude_func)

            if midi_notes is not None:
                try:
                    midi_note = midi_notes[i]
                except KeyError:
                    midi_note = None
            else:
                midi_note = None

            if assign_individual_materials:
                if i > 1:
                    bl_obj_material = obj_material_001.copy()
                    bl_obj_material.animation_data_clear()
                    bl_obj.active_material = bl_obj_material
                    nt_obj = MetaObject(bl_obj, bl_obj_material, midi_note)
                else:
                    nt_obj = MetaObject(bl_obj, None, midi_note)
            else:
                nt_obj = MetaObject(bl_obj, None, midi_note)

            self.object_list.append(nt_obj)

        self.obj_index = -1
        self.midi_notes = midi_notes

    def __iter__(self):
        return self

    def __next__(self):
        self.obj_index += 1
        if self.obj_index >= len(self.object_list):
            self.obj_index = -1
            raise StopIteration()
        else:
            return self.object_list[self.obj_index]

    def __index__(self, obj):
        return self.object_list.index(obj)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise IndexError("index must be an integer")

        if index <= -1:
            return self.object_list[index]
        if index == 0:
            raise IndexError("indices start at 1, not 0. Sorry for the confusion.")
        else:
            return self.object_list[index - 1]

    def get_obj_by_midi_note(self, index):
        if not isinstance(index, int):
            raise IndexError("index must be an integer")

        for key, val in self.midi_notes.items():
            if val == index:
                return self.object_list[key - 1]
        raise KeyError(f"no note object found for MIDI note {index}.")

    def get_index(self, obj):
        if not isinstance(obj, MetaObject):
            raise ValueError("obj must be an ObjectManager MetaObject")

        return self.object_list.index(obj) + 1
