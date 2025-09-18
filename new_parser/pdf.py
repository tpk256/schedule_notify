import os
import subprocess
from typing import Optional



def convert_excel_to_pdf(file_path: str, dest_dir_path: str) -> str:

    subprocess.run(
        ["soffice", "--headless", "--convert-to", "pdf", file_path, "--outdir", dest_dir_path],
            timeout=30,
            check=True
    )

    new_path_file = os.path.join(dest_dir_path, os.path.basename(file_path).replace('.xlsx', '.pdf'))
    return new_path_file

