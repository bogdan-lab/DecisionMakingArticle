import os
import random
from flask import Flask, render_template, request, redirect, url_for
from pathlib import Path
from time import time
import random
from collections import namedtuple
import uuid
from typing import List, Dict
import datetime


app = Flask(__name__)

def get_files_in_folder(path: Path, ext: str):
    file_names = os.listdir(path)
    result = []
    for el in file_names:
        if el.endswith(ext):
            result.append(Path(path, el))
    return result


FileIndex = namedtuple("FileIndex", "file index")
Experiment = namedtuple("Experiment", "id left_pic right_pic left_pic_val right_pic_val exposition_begin exposition_end selected_pic")

class ImageDisplayer:
 
    @staticmethod
    def shuffle_files(file_names):
        random.seed(int(time()))
        random.shuffle(file_names)

    def __init__(self, img_folder: str):
        static_path = Path("static", img_folder)
        self.image_paths = get_files_in_folder(static_path, '.png')
        self.shuffle_files(self.image_paths)
        self.image_meta = self.prepare_meta(get_files_in_folder(static_path, '.csv'))
        self.lhs_image = self.get_file_index(0)
        self.rhs_image = self.get_file_index(1)
        self.experiments = []
        self.append_experiment()

    def prepare_meta(self, paths: List[Path]) -> Dict[str, str]:
        if len(paths) == 0:
            return None
        if len(paths) > 1:
            raise RuntimeError(f"There are more than one meta file in image folder! Files I found: {paths}")
        res = {}
        with open(paths[0], 'r') as fin:
            for line in fin:
                line = line.strip()
                if line[0] == '#':
                    continue
                spl = line.split(',')
                res[spl[0]] = spl[1]
        return res


    def append_experiment(self):
        curr_time = time()
        lhs_pic = self.get_curr_lhs_image().name
        rhs_pic = self.get_curr_rhs_image().name
        self.experiments.append(Experiment(id=uuid.uuid4(), 
                                           left_pic=lhs_pic, 
                                           right_pic=rhs_pic,
                                           left_pic_val=self.image_meta[lhs_pic],
                                           right_pic_val=self.image_meta[rhs_pic],
                                           exposition_begin=curr_time,
                                           exposition_end=None,
                                           selected_pic=None))

    def finalize_experiment(self, chosen: str):
        if len(self.experiments) <= 0:
            return
        exposition_end = time()
        selected_image = self.get_curr_lhs_image().name if chosen == "LHS" else self.get_curr_rhs_image().name
        last_exp = self.experiments[-1]
        self.experiments[-1] = Experiment(id=last_exp.id,
                                          left_pic=last_exp.left_pic,
                                          right_pic=last_exp.right_pic,
                                          left_pic_val=last_exp.left_pic_val,
                                          right_pic_val=last_exp.right_pic_val,
                                          exposition_begin=last_exp.exposition_begin,
                                          exposition_end=exposition_end,
                                          selected_pic=selected_image)

    def get_file_index(self, index):
        return FileIndex(self.image_paths[index], index)
    
    def get_next_file_index(self):
        return self.get_file_index(max(self.lhs_image.index, self.rhs_image.index) + 1)

    def log_experiments(self):
        dt = datetime.datetime.fromtimestamp(time())
        dt_str = dt.strftime("%Y-%m-%d_%H_%M_%S")
        fname = f"{dt_str}_experiment_log.csv"
        with open(fname, 'w') as fout:
            fout.write("#id,left_pic,right_pic,left_pic_val,right_pic_val,exposition_begin,exposition_end,selected_pic\n")
            for v in self.experiments:
                fout.write(f"{v.id},{v.left_pic},{v.right_pic},{v.left_pic_val},{v.right_pic_val},{v.exposition_begin},{v.exposition_end},{v.selected_pic}\n")

    def get_curr_lhs_image(self):
        return self.lhs_image.file

    def get_curr_rhs_image(self):
        return self.rhs_image.file

    def change_images(self):
        self.lhs_image = self.get_next_file_index()
        self.rhs_image = self.get_next_file_index()


global image_displayer
image_displayer = ImageDisplayer("images")

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        selected_image = request.form['selected_image']
        if selected_image == "STOP":
            image_displayer.log_experiments()
            raise KeyboardInterrupt("Experiments were stopped by pressing STOP button")
        
        image_displayer.finalize_experiment(selected_image)
        image_displayer.change_images()
        image_displayer.append_experiment()
    return render_template('index.html', image_lhs=image_displayer.get_curr_lhs_image(), image_rhs=image_displayer.get_curr_rhs_image())

if __name__ == '__main__':
    app.run(debug=True)







