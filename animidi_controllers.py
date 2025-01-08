import animidi
import math
if __name__ != "__main__":
    import bpy

# hit react controller with optional overshoot
def hit_react_controller(
    note,
    track,

    target_object,
    data_path,
    index = None,
    exclude_func = None,

    match_note = True,
    val_function = None,
    time_before_all_other_notes = -100,
    time_after_all_other_notes = 1000000,

    resting_value = 0,

    pre_hit_t = 5,
    pre_hit_threshold = 50,

    handle_y = 0.1,

    enable_anti_climax_scaling = True,
    anti_climax_scaling_threshold = 6,

    anti_climax_t = 3,
    anti_climax_value = -1,
    anti_climax_threshold_multiplier = 2.5,

    enable_overshoot = True,
    overshoot_t = 10,
    overshoot_threshold = 20,
    overshoot_value = 1,

    settle_t = 15,
    settle_threshold = 20,
):
    #print("AHWOOG!")
    # Get Time To Previous Note and Time To Next Note
    next_note = animidi.get_next_note(
        track = track,
        note = note,
        direction = "next",
        match_note = match_note,
        val_function = val_function,
    )
    if next_note == None:
        TTNN = abs(note.note_on - time_after_all_other_notes)
    else:
        TTNN = abs(note.note_on - next_note.note_on)

    previous_note = animidi.get_next_note(
        track = track,
        note = note,
        direction = "previous",
        match_note = match_note,
        val_function = val_function,
    )
    if previous_note == None:
        TTPN = abs(note.note_on - time_before_all_other_notes)
    else:
        TTPN = abs(note.note_on - previous_note.note_on)

    # The pre-hit
    if TTPN >= pre_hit_threshold:
        animidi.insert_keyframe(
            target_object = target_object,
            data_path = data_path,
            index = index,
            frame = note.note_on - pre_hit_t,
            value = resting_value,
            exclude_func = exclude_func,
        )

    # The moment the hit happens, put a keyframe there
    animidi.insert_keyframe(
        target_object = target_object,
        data_path = data_path,
        index = index,
        frame = int(note.note_on),
        value = resting_value,
        handle_left_type = "FREE",
        #handle_left = [0, -0.25],
        handle_right_type = "FREE",
        handle_right = [0, handle_y],
        exclude_func = exclude_func,
    )

    # The anti-climax
    anti_climax_time = anti_climax_t
    if TTNN < (anti_climax_t * anti_climax_threshold_multiplier):
        anti_climax_time = TTNN / anti_climax_threshold_multiplier

    anti_climax_val = anti_climax_value
    if enable_anti_climax_scaling:
        if anti_climax_value > resting_value:
            anti_climax_val = animidi.scale_linear(TTNN, 0, anti_climax_scaling_threshold, resting_value, anti_climax_value, max=anti_climax_value, min=resting_value)
        elif anti_climax_value < resting_value:
            anti_climax_val = animidi.scale_linear(TTNN, 0, anti_climax_scaling_threshold, resting_value, anti_climax_value, max=resting_value, min=anti_climax_value)
        else:
            anti_climax_val = anti_climax_value

    animidi.insert_keyframe(
        target_object = target_object,
        data_path = data_path,
        index = index,
        frame = note.note_on + anti_climax_time,
        value = anti_climax_val,
        exclude_func = exclude_func,
    )

    # The overshoot
    if enable_overshoot:
        if TTNN >= overshoot_threshold:
            animidi.insert_keyframe(
                target_object = target_object,
                data_path = data_path,
                index = index,
                frame = note.note_on + overshoot_t,
                value = overshoot_value,
                exclude_func = exclude_func,
            )

    # The second settle
    if TTNN >= settle_threshold:
        animidi.insert_keyframe(
            target_object = target_object,
            data_path = data_path,
            index = index,
            frame = note.note_on + settle_t,
            value = resting_value,
            exclude_func = exclude_func,
        )

# With this one, remember to insert a default-off keyframe at the beginning
def flash_controller(
    note,
    track,

    target_object,
    data_path,
    index = None,
    exclude_func = None,

    match_note = True,
    val_function = None,
    time_before_all_other_notes = -100,
    time_after_all_other_notes = 1000000,

    on_value = 1,
    off_value = 0,
    flash_threshold = 2,
    cooldown_t = 5,
):
    # Get time to next note and time to previous note
    next_note = animidi.get_next_note(
        track = track,
        note = note,
        direction = "next",
        match_note = match_note,
        val_function = val_function,
    )
    if next_note == None:
        TTNN = abs(note.note_on - time_after_all_other_notes)
    else:
        TTNN = abs(note.note_on - next_note.note_on)

    previous_note = animidi.get_next_note(
        track = track,
        note = note,
        direction = "previous",
        match_note = match_note,
        val_function = val_function,
    )
    if previous_note == None:
        TTPN = abs(note.note_on - time_before_all_other_notes)
    else:
        TTPN = abs(note.note_on - previous_note.note_on)

    animidi.insert_keyframe(
        target_object = target_object,
        data_path = data_path,
        frame = int(note.note_on),
        value = on_value,
        interpolation = "LINEAR",
        exclude_func = exclude_func
    )

    if TTNN > flash_threshold:
        # Cooldown
        cooldown_value = animidi.scale_linear(TTNN - 1, 0, cooldown_t, on_value, off_value, max=on_value, min=off_value)
        cooldown_time = TTNN - 1
        if cooldown_time > cooldown_t:
            cooldown_time = cooldown_t

        #print(brightness)

        animidi.insert_keyframe(
            target_object = target_object,
            data_path = data_path,
            frame = note.note_on + cooldown_time,
            value = cooldown_value,
            interpolation = "CONSTANT",
            exclude_func = exclude_func
        )
