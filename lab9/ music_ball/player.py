import pygame
import os


class MusicPlayer:
    def __init__(self, music_folder):
        # путь к папке с музыкой
        self.music_folder = music_folder

        # список всех треков из папки
        self.playlist = self.load_tracks()

        # индекс текущего трека
        self.current_index = 0

        # играет музыка или нет
        self.is_playing = False

    def load_tracks(self):
        # создаем пустой список треков
        tracks = []

        # перебираем все файлы в папке music
        for file in os.listdir(self.music_folder):
            # если файл оканчивается на .mp3 или .wav
            if file.endswith(".mp3") or file.endswith(".wav"):
                # добавляем полный путь к файлу в список
                tracks.append(os.path.join(self.music_folder, file))

        return tracks

    def play(self):
        if not self.playlist:
            return

        pygame.mixer.music.load(self.playlist[self.current_index])

        pygame.mixer.music.play()

        self.is_playing = True

    def stop(self):

        pygame.mixer.music.stop()


        self.is_playing = False

    def next_track(self):

        if not self.playlist:
            return

        self.current_index = (self.current_index + 1) % len(self.playlist)

        self.play()

    def prev_track(self):

        if not self.playlist:
            return

        self.current_index = (self.current_index - 1) % len(self.playlist)

        self.play()

    def get_current_track_name(self):
        if not self.playlist:
            return "No tracks"

        return os.path.basename(self.playlist[self.current_index])