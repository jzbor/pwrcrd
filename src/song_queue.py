from song import SongJob

class Queue(list):
    def pop(self):
        super.pop(0)
