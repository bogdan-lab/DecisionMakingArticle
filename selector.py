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
from abc import ABC, abstractmethod

Image = namedtuple("Image", "path value")
Experiment = namedtuple("Experiment", "id left_pic right_pic left_pic_val right_pic_val exposition_begin exposition_end selected_pic")

app = Flask(__name__)

def get_files_in_folder(path: Path, ext: str) -> List[Path]:
    file_names = os.listdir(path)
    result = []
    for el in file_names:
        if el.endswith(ext):
            result.append(Path(path, el))
    return result

def shuffle_list(file_names):
    random.seed(int(time()))
    random.shuffle(file_names)


def read_meta_file(path: Path) -> Dict[str, str]:
    res = {}
    with open(path, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line[0] == '#':
                continue
            spl = line.split(',')
            res[spl[0]] = spl[1]
    return res



class DataSource(ABC):

    @abstractmethod
    def change_images(self) -> None:
        pass

    @abstractmethod
    def get_curr_lhs(self) -> Image:
        pass

    @abstractmethod
    def get_curr_rhs(self) -> Image:
        pass

class GeneratedImagesSource(DataSource):

    @staticmethod
    def buid_file_data(path: Path):
        image_paths = get_files_in_folder(path, '.png')
        meta_files = get_files_in_folder(path, '.csv')
        assert len(meta_files) == 1
        meta = read_meta_file(meta_files[0])
        result = []
        for img_path in image_paths:
            result.append(Image(path=img_path, value=meta[img_path.name]))
        shuffle_list(result)
        return result

    def __init__(self, path: Path):
        self.data = self.buid_file_data(path)
        self.lhs = self.acquire_last()
        self.rhs = self.acquire_last()
    
    def acquire_last(self) -> Image:
        img = self.data[-1]
        self.data.pop()
        return img
    
    def change_images(self) -> None:
        self.lhs = self.acquire_last()
        self.rhs = self.acquire_last()
    
    def get_curr_lhs(self) -> Image:
        return self.lhs
    
    def get_curr_rhs(self) -> Image:
        return self.rhs


class ImageDisplayer:

    def __init__(self, ds: DataSource):
        self.ds = ds
        self.experiments = []
        self.append_experiment()

    def append_experiment(self):
        curr_time = time()
        lhs_pic = self.ds.get_curr_lhs()
        rhs_pic = self.ds.get_curr_rhs()
        self.experiments.append(Experiment(id=uuid.uuid4(), 
                                           left_pic=lhs_pic.path.name, 
                                           right_pic=rhs_pic.path.name,
                                           left_pic_val=lhs_pic.value,
                                           right_pic_val=rhs_pic.value,
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

    def log_experiments(self):
        dt = datetime.datetime.fromtimestamp(time())
        dt_str = dt.strftime("%Y-%m-%d_%H_%M_%S")
        fname = f"{dt_str}_experiment_log.csv"
        with open(fname, 'w') as fout:
            fout.write("#id,left_pic,right_pic,left_pic_val,right_pic_val,exposition_begin,exposition_end,selected_pic\n")
            for v in self.experiments:
                fout.write(f"{v.id},{v.left_pic},{v.right_pic},{v.left_pic_val},{v.right_pic_val},{v.exposition_begin},{v.exposition_end},{v.selected_pic}\n")

    def get_curr_lhs_image(self):
        return self.ds.get_curr_lhs().path

    def get_curr_rhs_image(self):
        return self.ds.get_curr_rhs().path

    def change_images(self):
        self.ds.change_images()



data_source = GeneratedImagesSource(Path("static/images"))


global image_displayer
image_displayer = ImageDisplayer(data_source)

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







