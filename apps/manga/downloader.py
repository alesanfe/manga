import logging
import os
import re
import sys
import tempfile
import time
import zipfile
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from typing import Dict

import requests
from bs4 import BeautifulSoup
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from selenium import webdriver
from selenium.webdriver.common.by import By

logging.basicConfig(level=logging.INFO)


def get_soup(url: str) -> BeautifulSoup:
    """
    Get the HTML content of a webpage and parse it into a BeautifulSoup object.

    Parameters:
        url (str): The URL of the webpage to retrieve.

    Returns:
        BeautifulSoup: A BeautifulSoup object representing the parsed HTML content.
    """
    response = requests.get(url)
    return BeautifulSoup(response.text, 'html.parser')


def extract_title(soup: BeautifulSoup) -> str:
    """
    Extracts the title from a BeautifulSoup object.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup object containing the HTML.

    Returns:
        str: The extracted title.
    """
    return soup.find('div', class_='ttline').text.replace('Manga', '').strip()


def extract_chapters(soup: BeautifulSoup) -> Dict[int, str]:
    """
    Extracts the chapters from a BeautifulSoup object.

    Parameters:
        soup (BeautifulSoup): The BeautifulSoup object representing the HTML.

    Returns:
        dict: A dictionary mapping chapter numbers to chapter links.
    """
    sections = soup.find_all('ul', class_='sub_vol_ul')
    chapter_elements = []
    for section in sections:
        chapter_elements.extend(section.find_all('li'))
    chapter_links = {}
    for chapter_element in chapter_elements:
        link = chapter_element.find('a')['href']
        print(chapter_element.find('a')['title'])
        num_chapters = re.findall(r'\d+(?:\.\d+)?', chapter_element.find('a')['title'])
        if len(num_chapters) >= 1:
            num_chapter = max(num_chapters)
        else:
            posible_num_chapter = min(chapter_links.keys())
            if posible_num_chapter <= 0:
                num_chapter = posible_num_chapter - 1
            else:
                num_chapter = 0
        chapter_number = float(num_chapter)
        chapter_links[chapter_number] = link
    return chapter_links


def download_image(chapter_info: tuple, options: dict) -> str:
    """
    Downloads an image from a chapter link using the specified options.

    Parameters:
        chapter_info (tuple): A tuple containing the chapter link, the key, and the index.
        options (dict): A dictionary containing the options for the webdriver.

    Returns:
        str or None: The source of the downloaded image if successful, None otherwise.
    """
    chapter_link, key, i = chapter_info
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(chapter_link)
        time.sleep(5)
        image = driver.find_element(By.CLASS_NAME, "manga_pic")
        image_src = image.get_attribute('src')
        return image_src
    except Exception as e:
        logging.error(f"Error downloading image for chapter {key}-{i}: {e}")
        return None
    finally:
        driver.quit()


def download_chapter_images(chapter_links: Dict[int, str]) -> list:
    """
    Downloads images for each chapter from a list of chapter links.

    Parameters:
        chapter_links (dict): A dictionary containing chapter names as keys and chapter links as values.
        title (str): The title of the book.
        options (dict): A dictionary containing options for downloading the images.
        driver: The web driver instance used to navigate to the chapter links.

    Returns:
        list: A list of downloaded images for all chapters.
    """
    with ProcessPoolExecutor() as executor:
        futures = []
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Para ejecutar en segundo plano
        driver = webdriver.Chrome(options=options)
        for key, link in chapter_links.items():
            driver.get(link)
            last_chapter = driver.find_element(By.CLASS_NAME, "pic_download").text.split('/')[1]
            for i in range(1, int(last_chapter) + 1):
                chapter_link = link.replace('.html', '') + '-' + str(i) + '.html'
                logging.info(f"Downloading image for chapter {key}-{i}")
                future = executor.submit(download_image, (chapter_link, key, i), options)
                futures.append(future)
        images = [future.result() for future in futures if future.result() is not None]
        driver.quit()
        logging.info("Downloaded all images successfully")
        return images


def create_pdf(images: list) -> BytesIO:
    """
    Creates a PDF file from a list of image URLs.

    Parameters:
        images (list): A list of strings representing the URLs of the images to include in the PDF.

    Returns:
        BytesIO: A BytesIO object containing the generated PDF data.

    Raises:
        Exception: If there is an error creating the PDF or removing temporary files.
    """
    pdf_data = BytesIO()
    c = canvas.Canvas(pdf_data, pagesize=letter)
    width, height = letter
    with ProcessPoolExecutor() as executor:
        temp_files = []
        try:
            for image_url in images:
                response = executor.submit(requests.get, image_url).result()
                if response.status_code == 200:
                    img_data = BytesIO(response.content)
                    _, temp_file = tempfile.mkstemp(suffix=".png")
                    temp_files.append(temp_file)
                    with open(temp_file, 'wb') as temp_file_stream:
                        temp_file_stream.write(img_data.getvalue())
                    c.drawImage(temp_file, 0, 0, width, height)
                    c.showPage()
                    logging.info(f"Added image to PDF: {image_url}")
                else:
                    logging.error(f"Failed to download image: {image_url}")
        except Exception as e:
            logging.error(f"Error creating PDF: {e}")
        finally:
            for temp_file in temp_files:
                try:
                    os.remove(temp_file)
                except Exception as e:
                    logging.error(f"Error removing temporary file {temp_file}: {e}")

    c.save()
    logging.info('PDF generated')
    pdf_data.seek(0)

    return pdf_data




def download_selected_chapters(manga: str, chapters: list) -> dict:
    """
    Downloads the selected chapters of a manga.

    Parameters:
        manga (str): The name of the manga.
        chapters (list): A list of chapter numbers to download.

    Returns:
        dict: A dictionary mapping PDF filenames to BytesIO objects containing the PDF data.
    """
    url = f'https://my.ninemanga.com/manga/{manga}.html?waring=1'
    try:
        soup = get_soup(url)
        manga_title = extract_title(soup)
        chapter_links = extract_chapters(soup)
        dic_chapter = {}
        for chapter_number, link in chapter_links.items():
            if int(chapter_number) in chapters:
                chapter_images = download_chapter_images({chapter_number: link})
                pdf_filename = f'{manga_title} Chapter {chapter_number}.pdf'
                dic_chapter[pdf_filename] = create_pdf(chapter_images)
        return dic_chapter
    except Exception as e:
        logging.error(f"Error downloading chapters: {e}")


def download_range_of_chapters(manga: str, start_chapter: int, end_chapter: int) -> dict:
    """
    Download all chapters of a manga.

    Parameters:
        manga (str): The name of the manga to download.

    Returns:
        dict: A dictionary mapping PDF filenames to BytesIO objects containing the PDF data.
    """
    return download_selected_chapters(manga, range(start_chapter, end_chapter + 1))


def download_all_chapters(manga: str) -> dict:
    """
    Download all chapters of a manga.

    Parameters:
        manga (str): The name of the manga to download chapters from.

    Returns:
        dict: A dictionary mapping PDF filenames to BytesIO objects containing the PDF data.
    """
    return download_selected_chapters(manga, range(-sys.maxsize, sys.maxsize))


def create_zip(pdf_data_dic: dict) -> BytesIO:
    """
    Crea un archivo ZIP que contiene varios archivos PDF.

    Parameters:
        pdf_data_dic (dict): Un diccionario donde las claves son títulos y los valores son datos de archivos PDF (BytesIO).

    Returns:
        BytesIO: Un BytesIO que contiene los datos del archivo ZIP.
    """
    try:
        # Crear un BytesIO para almacenar el archivo ZIP
        zip_buffer = BytesIO()

        # Crear un objeto ZipFile en modo escritura
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Agregar cada PDF al archivo ZIP
            for title, pdf_data in pdf_data_dic.items():
                # Agregar el PDF al archivo ZIP con el nombre del título
                zip_file.writestr(title, pdf_data.getvalue())

        # Mover el puntero del BytesIO al principio
        zip_buffer.seek(0)

        return zip_buffer
    except Exception as e:
        # Manejar cualquier error que pueda ocurrir durante la creación del archivo ZIP
        print(f"Error al crear el archivo ZIP: {e}")
        return None


