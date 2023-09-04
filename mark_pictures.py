import os
from pathlib import Path
from typing import List

# PATH = Path("cats and dogs/cats")
# VALUE = "cat"

PATH = Path("cats and dogs/dogs")
VALUE = "dog"

def get_pic_names(path: Path) -> List[str]:
    pic_ext = {'.png', '.jpg'}
    names = os.listdir(path)
    result = []
    for el in names:
        if any(el.endswith(ext) for ext in pic_ext):
            result.append(el)
    return result



def mark_pictures(path: Path, value: str):
    my_pictures = get_pic_names(path)
    with open(Path(path, "catdogs_meta.csv"), 'w') as fout:
        fout.write('\n'.join(f"{name},{VALUE}" for name in my_pictures))


def main():
    mark_pictures(PATH, VALUE)
    




if __name__ == "__main__":
    main()