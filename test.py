from mido import Message, MidiFile, MidiTrack, bpm2tempo, MetaMessage

# Mapping des notes vers numéros MIDI (do = 60)
note_mapping = {
    'do': 60,
    're': 62,
    'mi': 64,
    'sol': 55,  # une octave plus bas
    'la': 57,   # une octave plus bas
    'si': 59    # une octave plus bas
}

# Durées en ticks (480 ticks = noire)
ticks_per_beat = 480
durations = {
    'noire': ticks_per_beat,
    'blanche': ticks_per_beat * 2,
    'ronde': ticks_per_beat * 4
}

# Séquence des notes : (note, durée)
notes_sequence = [
    ('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('la', 'blanche'), ('la', 'blanche'),
    ('re', 'noire'), ('do', 'noire'), ('si', 'noire'), ('la', 'noire'), ('sol', 'ronde'),
    
	('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('la', 'blanche'), ('la', 'blanche'),
    ('re', 'noire'), ('do', 'noire'), ('si', 'noire'), ('la', 'noire'), ('sol', 'ronde'),
    
	('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('la', 'blanche'), ('la', 'blanche'),
    ('re', 'noire'), ('do', 'noire'), ('si', 'noire'), ('la', 'noire'), ('sol', 'ronde'),
    
	('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('do', 'noire'), ('do', 'noire'), ('do', 'noire'), ('re', 'noire'), ('mi', 'blanche'), ('re', 'blanche'),
    ('do', 'noire'), ('mi', 'noire'), ('re', 'noire'), ('re', 'noire'), ('do', 'ronde'),

    ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('re', 'noire'), ('la', 'blanche'), ('la', 'blanche'),
    ('re', 'noire'), ('do', 'noire'), ('si', 'noire'), ('la', 'noire'), ('sol', 'ronde')
]

# Création du fichier MIDI
mid = MidiFile(ticks_per_beat=ticks_per_beat)
track = MidiTrack()
mid.tracks.append(track)

# Tempo (90 bpm)
tempo = bpm2tempo(90)
track.append(MetaMessage('set_tempo', tempo=tempo, time=0))

# Instrument (piano)
track.append(Message('program_change', program=0, time=0))

# Ajouter les notes
for note, duration in notes_sequence:
    note_number = note_mapping[note]
    duration_ticks = durations[duration]
    track.append(Message('note_on', note=note_number, velocity=64, time=0))
    track.append(Message('note_off', note=note_number, velocity=64, time=duration_ticks))

# Sauvegarder le fichier MIDI
mid.save('audio.mid')
print("Fichier MIDI généré : audio.mid")
