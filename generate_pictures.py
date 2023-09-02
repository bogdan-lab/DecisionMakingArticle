from abc import ABC, abstractmethod
from pathlib import Path
import numpy as np
import pygame
from pygame.locals import *
import matplotlib.pyplot as plt
import time
import datetime


class Generator(ABC):
    
    @abstractmethod
    def generate_images(self, n: int, path: Path) -> None:
        pass


def get_timestamp_s() -> int:
    return int(time.mktime(datetime.datetime.today().timetuple()))

def get_float_rnd(start: float, end: float, n: int):
    np.random.seed(get_timestamp_s())
    return start + np.random.rand(n)*(end - start)

def get_int_rnd(start: int, end: int, n: int):
    return get_float_rnd(start, end, n).astype(int)
    

class NumberGenerator(Generator):
    
    def __init__(self, min_val: int, max_val: int, pic_width: int, pic_height: int) -> None:
        self.min_val = min_val
        self.max_val = max_val
        self.pic_width = pic_width
        self.pic_height = pic_height
        self.name_tag = "number"
        self.background_color = (255, 255, 255)
        self.text_color = (0, 0, 0)

    def create_picture(self, value: int, name: str, path: Path) -> None:
        pygame.init()
        screen = pygame.Surface((self.pic_width, self.pic_height))
        screen.fill(self.background_color)
        font = pygame.font.Font(None, 130)
        number = str(value)
        text_image = font.render(number, True, self.text_color)
        text_position = (10, self.pic_height/2 - 40)
        screen.blit(text_image, text_position)
        pygame.image.save(screen, Path(path, name))
        pygame.quit()
   

    def save_meta_data(self, values, pic_fnames, name: str, path: Path)->None:
        with open(Path(path, name), 'w') as fout:
            fout.write('\n'.join(f"{fname},{v}" for (fname, v) in zip(pic_fnames, values)))

    def generate_images(self, n: int, path: Path) -> None:
        values = get_int_rnd(self.min_val, self.max_val, n)
        pic_fnames = []
        for i, el in enumerate(values):
            fname = f"{self.name_tag}_{get_timestamp_s()}_{i}.png"
            self.create_picture(el, fname, path)
            pic_fnames.append(fname)
        self.save_meta_data(values, pic_fnames, f"{self.name_tag}_meta_{get_timestamp_s()}.csv", path)



class AngleGenerator(Generator):
    
    def __init__(self, pic_width, pic_height) -> None:
        self.name_tag = "angle"
        self.pic_width = pic_width
        self.pic_height = pic_height

    def create_picture(self, sin_val: float, cos_val: float, name: str, path: Path) -> None:
        dpi = 300
        dots = np.array([[1,0], [0, 0], [cos_val, sin_val]])
        plt.figure(figsize=(self.pic_width/dpi, self.pic_height/dpi), dpi=dpi)
        plt.xlim(-1.1, 1.1)
        plt.ylim(-0.5, 1.1)
        plt.axis('off')
        plt.plot(dots[:,0], dots[:,1], '-', marker='.', markersize=8, color="black", lw=3)
        plt.savefig(Path(path, name), dpi=dpi)
        plt.close()

    def save_meta_data(self, values, pic_fnames, name: str, path: Path)->None:
        with open(Path(path, name), 'w') as fout:
            fout.write('\n'.join(f"{fname},{v}" for (fname, v) in zip(pic_fnames, values)))

    def generate_images(self, n: int, path: Path) -> None:
        cos_values = get_float_rnd(-1, 1, n)
        sin_values = np.sqrt(1 - cos_values*cos_values)
        pic_fnames = []
        for i, (s, c) in enumerate(zip(sin_values, cos_values)):
            fname = f"{self.name_tag}_{get_timestamp_s()}_{i}.png"
            self.create_picture(s, c, fname, path)
            pic_fnames.append(fname)
        self.save_meta_data(cos_values, pic_fnames, f"{self.name_tag}_meta_{get_timestamp_s()}.csv", path)


if __name__ == "__main__":
    DIR_PATH = Path("/home/bohdan/workplace/Bibliotech/Python/DecisionMakingArticle")
    WIDTH = 400
    HEIGHT = 300

    num_gen = NumberGenerator(min_val=1_000_000, max_val=2_000_000, pic_width=WIDTH, pic_height=HEIGHT)
    num_gen.generate_images(3, DIR_PATH)

    ang_gen = AngleGenerator(pic_width=WIDTH, pic_height=HEIGHT)
    ang_gen.generate_images(3, DIR_PATH)
