import os
import random
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from time import time
import random
from collections import namedtuple


app = Flask(__name__)

def get_files_in_folder(path: Path, ext: str):
    file_names = os.listdir(path)
    result = []
    for el in file_names:
        if el.endswith(ext):
            result.append(Path(path, el))
    return result


FileIndex = namedtuple("FileIndex", "file index")

class ImageDisplayer:
 
    @staticmethod
    def shuffle_files(file_names):
        random.seed(int(time()))
        random.shuffle(file_names)

    def __init__(self, img_folder: str):
        static_path = Path("static", img_folder)
        self.image_paths = get_files_in_folder(static_path, '.png')

        print("Files: ", self.image_paths)

        self.shuffle_files(self.image_paths)
        self.image_meta = get_files_in_folder(static_path, '.csv')[0]
        self.lhs_image = self.get_file_index(0)
        self.rhs_image = self.get_file_index(1)

    def get_file_index(self, index):
        return FileIndex(self.image_paths[index], index)
    
    def get_next_file_index(self):
        return self.get_file_index(max(self.lhs_image.index, self.rhs_image.index) + 1)

    def log_event(self):
        pass

    def get_curr_lhs_image(self):
        return self.lhs_image.file

    def get_curr_rhs_image(self):
        return self.rhs_image.file

    def change_lhs_image(self):
        self.lhs_image = self.get_next_file_index()

    def change_rhs_image(self):
        self.rhs_image = self.get_next_file_index()


global image_displayer
image_displayer = ImageDisplayer("images")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_image = request.form['selected_image']
        if selected_image == "LHS":
            image_displayer.change_rhs_image()
        else:
            image_displayer.change_lhs_image()
    return render_template('index.html', image_lhs=image_displayer.get_curr_lhs_image(), image_rhs=image_displayer.get_curr_rhs_image())

if __name__ == '__main__':
    app.run(debug=True)