import os
from pdf2image import convert_from_path



def convert_pdf_to_jpgs(pdf_path: str, dest_dir_path: str, suffix: str, dpi=300) -> list[str]:

    images = convert_from_path(pdf_path, dpi=dpi)
    paths = []

    for i, image in enumerate(images):
        path_jpg = os.path.join(dest_dir_path, f"{suffix}_page_{i + 1}.jpg")
        image.save(path_jpg, "JPEG")
        paths.append(path_jpg)

    return paths
