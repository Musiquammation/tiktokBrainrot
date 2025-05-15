import pygame
from screen import *
from game import Game


pygame.init()
game = Game()


FPS = 60
CREATE_VIDEO = True

if CREATE_VIDEO:
	import moviepy.editor as mpy
	import mido
	from mido import MidiFile, MidiTrack, Message
	from midi2audio import FluidSynth
	from moviepy.editor import VideoFileClip, AudioFileClip


	VIDEO_DURATION = 62
	
	FILE_SOUNDFONT = 'audio/FluidR3_GM.sf2'
	FILE_MIDI = "audio/au_clair_de_la_lune.mid"
	FILE_NEW_MIDI = 'output/midi.mid'
	FILE_AUDIO = 'output/audio.wav'
	FILE_VIDEO = 'output/video.mp4'
	FILE_FINAL = 'output/output.mp4'


	TICKS_PER_BEAT = 480
	TEMPO = mido.bpm2tempo(120)  # 120 BPM = 500000 µs par beat
	NOTE_DURATION = TICKS_PER_BEAT*2  # Durée d'une croche = 240 ticks



	def read_midi():
		midi = MidiFile(FILE_MIDI)
		notes = []
		time = 0
		for track in midi.tracks:
			for msg in track:
				time += msg.time
				if msg.type == 'note_on' and msg.velocity > 0:
					notes.append({'note': msg.note, 'time': time, 'velocity': msg.velocity})
		return notes


	def create_midi(new_notes):
		new_midi = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
		track = MidiTrack()
		new_midi.tracks.append(track)

		track.append(mido.MetaMessage('set_tempo', tempo=TEMPO))

		tempTrack: list[Message] = []

		class Msg:
			def __init__(self, id, note, velocity, time):
				self.id = id
				self.note = note
				self.velocity = velocity
				self.time = time

		tempTrack: list[Msg] = []

		for note in new_notes:
			tempTrack.append(Msg('note_on', note['note'], note['velocity'], note['time']))
			# tempTrack.append(Msg('note_off', note['note'], 0, note['time'] + NOTE_DURATION*2))

		tempTrack.sort(key=lambda msg: msg.time)


		for i in range(0, len(tempTrack)):
			if tempTrack[i].id == 'note_on':
				print("Play", tempTrack[i].note, "at", tempTrack[i].time)

			track.append(Message(
				tempTrack[i].id,
				note=tempTrack[i].note,
				velocity=tempTrack[i].velocity,
				time=tempTrack[i].time - (0 if i == 0 else tempTrack[i-1].time)
			))



		new_midi.save(FILE_NEW_MIDI)


	def generate_audio_from_midi():
		fs = FluidSynth(FILE_SOUNDFONT)
		fs.midi_to_audio(FILE_NEW_MIDI, FILE_AUDIO)
		print(f"Audio file saved at : {FILE_AUDIO}")




	notes = read_midi()
	new_notes = []

	# Fonction pour générer une frame
	def generate_frame(t):
		screen = pygame.Surface((WIDTH, HEIGHT))
		screen.fill((0, 0, 0))

		# Calculer le temps en ticks basé sur game.frame
		game_tick_time = int((game.frame / FPS) * (TICKS_PER_BEAT * 120 / 60))  # fps → ticks conversion

		# Si le jeu renvoie True et qu'il reste des notes
		if game.run() and notes:
			note = notes.pop(0)
			note['time'] = game_tick_time
			new_notes.append(note)

		game.draw(screen)
		game.frame += 1
		return screen

	# Créer la vidéo
	def create_video():
		def make_frame(t):
			screen = generate_frame(t)
			return pygame.surfarray.array3d(screen).swapaxes(0, 1)

		clip = mpy.VideoClip(make_frame, duration=VIDEO_DURATION)
		clip.fps = FPS
		clip.write_videofile(FILE_VIDEO, codec='libx264')

	create_video()

	# Générer le MIDI synchronisé
	create_midi(new_notes)

	# Générer l'audio
	generate_audio_from_midi()

	# Ajouter le son à la vidéo
	video = VideoFileClip(FILE_VIDEO)
	audio = AudioFileClip(FILE_AUDIO)
	min_duration = min(video.duration, audio.duration)
	video_with_audio = video.set_audio(audio.subclip(0, min_duration))
	video_with_audio.write_videofile(FILE_FINAL, codec="libx264", audio_codec="aac")



else:
	# Mode visualisation temps réel (sans vidéo)
	screen = pygame.display.set_mode((WIDTH, HEIGHT))
	pygame.display.set_caption("Brainrot")

	clock = pygame.time.Clock()
	running = True

	while running:
		screen.fill((0, 0, 0))

		game.run()
		game.draw(screen)
		game.frame += 1

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				running = False

		pygame.display.flip()
		clock.tick(FPS)

	pygame.quit()
