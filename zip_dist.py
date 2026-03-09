import shutil
import os

source_dir = os.path.join('dist', 'AudioTranscriber')
output_filename = os.path.join('dist', 'AudioTranscriber')

if os.path.exists(source_dir):
    print(f"Zipping {source_dir} to {output_filename}.zip")
    shutil.make_archive(output_filename, 'zip', source_dir)
    print("Zipping complete.")
else:
    print(f"Error: {source_dir} not found.")
