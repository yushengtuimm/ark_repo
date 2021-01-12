import os


class Mixin:
    def download_csv(self, dir):
        resp = self.execute()
        with open(os.path.join(dir, self.filename), "wb") as file:
            file.write(resp)