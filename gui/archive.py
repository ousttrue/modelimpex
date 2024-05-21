import zipfile
import pathlib


HERE = pathlib.Path(__file__).absolute().parent


def process_archive(archive: pathlib.Path):
    print(archive)
    try:
        with zipfile.ZipFile(archive, metadata_encoding="GB2312") as zf:
            names = zf.namelist()
            for name in names:
                if name.endswith(".pmx"):
                    print(f"  {name}")
    except:
        with zipfile.ZipFile(archive) as zf:
            names = zf.namelist()
            for name in names:
                if name.endswith(".pmx"):
                    print(f"  {name}")


def process(dir: pathlib.Path):
    for child in dir.iterdir():
        if child.is_dir():
            process(child)
        else:
            if child.suffix == ".zip":
                process_archive(child)


if __name__ == "__main__":
    process(HERE)
