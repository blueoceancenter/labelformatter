import os
import time
from PyPDF2 import PdfReader
import fitz  # PyMuPDF
from PIL import Image
import argparse
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


def points_to_inches(points):
    return points / 72


def split_image_along_long_edge_and_calculate(binary_image, parts=10):
    width, height = binary_image.size
    part_height = height // parts
    total_area = width * height

    content_ratios = []

    for i in range(parts):
        upper = i * part_height
        lower = (i + 1) * part_height if i < (parts - 1) else height
        part_image = binary_image.crop((0, upper, width, lower))
        part_bbox = part_image.getbbox()

        part_content_area = (
            (part_bbox[2] - part_bbox[0]) * (part_bbox[3] - part_bbox[1])
            if part_bbox
            else 0
        )
        part_content_ratio = (
            (part_content_area / total_area) * 100 if total_area > 0 else 0
        )
        content_ratios.append(part_content_ratio)

    return round(sum(content_ratios), 1)


def calculate_content_ratio(pdf_file):
    doc = fitz.open(pdf_file)
    page = doc.load_page(0)
    pix = page.get_pixmap(matrix=fitz.Matrix(300 / 72, 300 / 72))
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

    gray_image = img.convert("L")
    threshold = 200
    binary_image = gray_image.point(lambda x: 0 if x > threshold else 255, "1")

    return split_image_along_long_edge_and_calculate(binary_image)


def classify_pdf(filename, folder_path):
    filepath = os.path.join(folder_path, filename)

    try:
        reader = PdfReader(filepath)
        first_page = reader.pages[0]
        mediabox = first_page.mediabox
        width = float(mediabox.width)
        height = float(mediabox.height)
        width_in = points_to_inches(width)
        height_in = points_to_inches(height)
        long_edge = max(width_in, height_in)
        short_edge = min(width_in, height_in)

        if long_edge < 7.5 and short_edge < 4.5:
            return "4x6"

        content_ratio = calculate_content_ratio(filepath)
        return "4x6" if content_ratio > 63 else "letter"

    except Exception as e:
        print(f"处理 PDF 文件时出错: {filename}，错误: {e}")
        return None


def already_processed(filename):
    filename = os.path.basename(filename)
    return filename.startswith("4x6_") or filename.startswith("letter_")


def process_file(filepath):
    folder_path, filename = os.path.split(filepath)

    if already_processed(filename):
        return

    if filename.lower().endswith(".pdf"):
        tag = classify_pdf(filename, folder_path)
    else:
        tag = "4x6"  # 默认非 PDF 文件标记为 4x6

    if tag:
        new_filename = f"{tag}_{filename}"
        new_filepath = os.path.join(folder_path, new_filename)
        os.rename(filepath, new_filepath)
        print(f"已将 '{filename}' 重命名为 '{new_filename}'")


def rename_pdfs(folder_path):
    for filename in os.listdir(folder_path):
        filepath = os.path.join(folder_path, filename)

        # 忽略文件夹
        if not os.path.isfile(filepath):
            continue

        process_file(filepath)


class FileMonitor(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory and not already_processed(event.src_path):
            print(f"检测到新文件: {event.src_path}")
            # Add a small delay to ensure the file is fully written
            time.sleep(1)
            process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory and not already_processed(event.dest_path):
            print(f"检测到文件移动: {event.dest_path}")
            # Add a small delay to ensure the file is fully written
            time.sleep(1)
            process_file(event.dest_path)


def monitor_folders(folders):
    observer = Observer()
    event_handler = FileMonitor()

    for folder in folders:
        print(f"开始监控文件夹: {folder}")
        observer.schedule(event_handler, folder, recursive=False)

        # Process existing files first
        print(f"处理现有文件...")
        rename_pdfs(folder)

    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Monitor folders and rename files based on content"
    )
    parser.add_argument(
        "--folders",
        nargs="+",
        type=str,
        required=True,
        help="Paths to the folders to monitor",
    )
    args = parser.parse_args()

    monitor_folders(args.folders)
