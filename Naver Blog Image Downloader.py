from bs4 import BeautifulSoup as bs
from PIL import Image
import urllib.request as req
from selenium import webdriver
from urllib.parse import parse_qs
import urllib.parse as parse
import requests
import time
import os

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from PyQt5.QtGui import *
import sys

import cv2
import numpy as np

global img_urls
global number_of_imgs
global make_folder_status
global post_title
global ext
last_download_path = "./"
special_characters = ["/", "?", '"', "'", "<", ">", "＼", "-", "  ", "*", ":"]


def CombineImage(raw_imgs):
    max_height, max_width = 0, 0
    for raw_img in raw_imgs:
        if np.shape(raw_img)[0] > max_height:
            max_height = np.shape(raw_img)[0]
        if np.shape(raw_img)[1] > max_width:
            max_width = np.shape(raw_img)[1]
    print(f"min_height: {max_height}\nmin_width: {max_width}")

    combined_img = np.array([])
    for raw_img_num, raw_img in enumerate(raw_imgs):
        height = np.shape(raw_img)[0]
        width = np.shape(raw_img)[1]
        print(f"height: {height}\nwidth: {width}")

        gap = max_width / width

        new_height = int(height * gap)
        new_width = int(max_width)
        print(f"new_height: {new_height}\nnew_width: {new_width}\n")

        processed_img = cv2.resize(raw_img, dsize=(new_width, new_height))
        if raw_img_num == 0:
            combined_img = processed_img
        else:
            combined_img = np.append(combined_img, processed_img, axis=0)

    return combined_img


def image_resize(width, height, max_length):
    if width >= height:
        gap = max_length / width
        new_width = int(width * gap)
        new_height = int(height * gap)

        print("new width & height: ", new_width, new_height)

        return new_width, new_height

    elif width < height:
        gap = max_length / height
        new_width = int(width * gap)
        new_height = int(height * gap)

        print("new width & height: ", new_width, new_height)

        return new_width, new_height


class DownloadModule:
    def __init__(self):
        self.page_title = ""

    def blog_post_image_finder(self, m_blog_url):
        url = m_blog_url

        req_get = requests.get(url=url)
        if req_get.status_code != 200:
            print("접속 오류 발생\ncode: ", req_get.status_code)
            return

        os.system("cls")
        print(f"{url}로 접속 성공!")

        html = req_get.text
        soup = bs(html, "html.parser")

        self.page_title = soup.find("meta", property="og:title")["content"]

        all_img = soup.find_all("img")
        count = 0
        img_src = list()
        for img in all_img:
            if img.get("data-lazy-src"):
                img_src.append(img.get("data-lazy-src"))
                count += 1

        if count == 0:
            chrome_webdriver_path = "chromedriver.exe"
            chrome_webdriver_options = webdriver.ChromeOptions()
            chrome_webdriver_options.add_argument(argument="headless")
            chrome_webdriver_options.add_argument(argument="disable-gpu")
            chrome_webdriver_options.add_argument(argument="window-size=1920x1080")

            chrome_webdriver = webdriver.Chrome(chrome_webdriver_path, options=chrome_webdriver_options)
            chrome_webdriver.get(url)
            html = chrome_webdriver.page_source

            soup = bs(html, "lxml")
            div = soup.find("div", {"id": "viewTypeSelector"})
            spans = div.find_all("span")
            print(f"length of spans: {len(spans)}")
            if len(spans) == 0:
                return self.page_title, img_src, count
            imgs = div.find_all("img")
            count = 0
            for img in imgs:
                img_url = img.get("src")
                if img_url == "https://ssl.pstatic.net/static/blank.gif":
                    print("Skip blank.gif")
                    continue
                img_src.append(img_url)
                count += 1
            print(f"이미지 개수: {count}")

            chrome_webdriver.close()
            return self.page_title, img_src, count

        print(f"이미지 개수: {len(img_src)}")
        return self.page_title, img_src, count


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.err = None
        self.cd = None
        self.spw = None

        self.fname = None

        self.grid = QGridLayout()
        self.setWindowTitle("Naver Blog Image Downloader")

        self.post_btn = QRadioButton("Post", self)
        self.post_btn.setChecked(True)

        self.cat_btn = QRadioButton("Category", self)

        self.url_label = QLabel("Post URL: ")

        self.m_blog_url = QLineEdit()

        self.make_folder = QCheckBox("Make Folder", self)
        self.img_combine = None
        self.post_num = None

        self.initUI()

    def initUI(self):
        self.setLayout(self.grid)

        self.grid.addWidget(self.post_btn, 0, 0)
        self.post_btn.clicked.connect(self.radioMethod)
        self.grid.addWidget(self.cat_btn, 0, 1)
        self.cat_btn.clicked.connect(self.radioMethod)

        self.grid.addWidget(self.url_label, 1, 0)
        self.grid.addWidget(self.m_blog_url, 1, 1)

        self.make_folder.setChecked(True)
        self.grid.addWidget(self.make_folder, 2, 0)

        main_btn = QPushButton("Done", self)
        main_btn.clicked.connect(self.btn1Method)
        self.grid.addWidget(main_btn, 3, 1)

    def radioMethod(self):
        if self.post_btn.isChecked() is True:
            self.grid.removeWidget(self.url_label)
            self.url_label.deleteLater()
            self.url_label = QLabel("Post URL: ")
            self.grid.addWidget(self.url_label, 1, 0)

            self.grid.removeWidget(self.post_num)
            self.post_num.deleteLater()

            self.grid.removeWidget(self.img_combine)
            self.img_combine.deleteLater()

        elif self.cat_btn.isChecked() is True:
            self.img_combine = QCheckBox("Combine posts images", self)
            self.grid.addWidget(self.img_combine, 2, 1)
            self.img_combine.setChecked(False)

            self.post_num = QCheckBox("Add post number", self)
            self.post_num.setChecked(False)
            self.grid.addWidget(self.post_num, 3, 0)

            self.grid.removeWidget(self.url_label)
            self.url_label.deleteLater()
            self.url_label = QLabel("Category URL: ")
            self.grid.addWidget(self.url_label, 1, 0)

    def btn1Method(self):
        global img_urls
        global number_of_imgs
        global make_folder_status
        global post_title
        global ext

        print(f"Make Folder status: {self.make_folder.isChecked()}")
        print(f"post_btn status: {self.post_btn.isChecked()}")
        print(f"cat_btn status: {self.cat_btn.isChecked()}")
        blog_url = self.m_blog_url.text()

        parsed_url = list(parse.urlparse(blog_url))
        if parsed_url[1] != "m.blog.naver.com":
            parsed_url[1] = "m.blog.naver.com"
        blog_url = parse.urlunparse(parsed_url)

        print(f"Blog URL: {blog_url}")
        make_folder_status = self.make_folder.isChecked()

        if self.post_btn.isChecked() is False:
            self.close()
            self.cd = CategoryDownload(blog_url=blog_url,
                                       img_combine_status=self.img_combine.isChecked(),
                                       post_num_status=self.post_num.isChecked())

        else:
            print("status_code:", requests.get(blog_url).status_code)

            dm = DownloadModule()
            try:
                post_title, img_urls, number_of_imgs = dm.blog_post_image_finder(blog_url)
            except Exception as e:
                print(e)
                self.err = ErrorPage("URLError")
                self.err.show()

                self.close()

            for special_character in special_characters:
                post_title = post_title.replace(special_character, "")
            print("post title:", post_title)

            if number_of_imgs == 0:
                self.err = ErrorPage("NO_IMAGE")
                self.err.show()

                self.close()

            else:
                self.spw = ShowPicWindow()
                self.spw.show()

                self.close()


class CategoryDownload(QWidget):
    def __init__(self, blog_url: str, img_combine_status: bool, post_num_status: bool):
        super().__init__()
        self.setWindowTitle("Category Downloading...")

        self.blog_url = blog_url
        self.fname = None
        self.dir_loc = None

        self.img_combine_status = img_combine_status
        self.post_num_status = post_num_status
        self.return_signal = False

        self.setFixedSize(320, 60)

        self.pbar = QProgressBar(self)
        self.pbar.setGeometry(10, 10, 300, 40)
        self.pbar.setMaximum(0)
        self.pbar.setMinimum(0)

        self.mw = MainWindow()
        self.err_page = None

        self.show()
        self.initUI()

    def initUI(self):
        global last_download_path
        global img_urls
        global number_of_imgs
        global make_folder_status
        global post_title
        global ext

        if ("categoryNo" in self.blog_url) is False:
            print("URL error")
            self.close()
            self.err_page = ErrorPage(code="URLError")
            self.err_page.show()
        else:
            chrome_driver_loc = "chromedriver.exe"
            chrome_driver_options = webdriver.ChromeOptions()
            chrome_driver_options.add_argument(argument="headless")
            chrome_driver_options.add_argument(argument="window-size=1920x1080")
            chrome_driver_options.add_argument(argument="disable-gpu")

            chrome_driver = webdriver.Chrome(chrome_driver_loc, options=chrome_driver_options)

            chrome_driver.get(self.blog_url)
            time.sleep(1)

            last_height = chrome_driver.execute_script("return document.body.scrollHeight")
            time.sleep(3)
            viewer_mode = chrome_driver.find_element_by_xpath("/html/body/ui-view/bg-nsc/div[9]/div[6]/div/div[1]/div/button[1]")
            viewer_mode.click()

            scroll_count = 0
            while True:
                QApplication.processEvents()
                print("scroll_count:", scroll_count)
                chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.2)
                new_height = chrome_driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    time.sleep(2)
                    chrome_driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    new_height = chrome_driver.execute_script("return document.body.scrollHeight")
                    if new_height == last_height:
                        break
                last_height = new_height
                scroll_count += 1

            html = chrome_driver.page_source
            soup = bs(html, "html.parser")

            category_title = chrome_driver.find_element_by_xpath(xpath="/html/body/ui-view/bg-nsc/div[9]/div[6]/div/div[1]/h3/a/span").text
            for special_character in special_characters:
                category_title = category_title.replace(special_character, "")

            chrome_driver.close()

            self.pbar.setMaximum(100)

            ul = soup.find("ul", {"class": "photo_list"})

            bloger_id = None
            post_ids = list()
            total_post_cnt = 0
            for li_num, li in enumerate(ul.find_all("li")):
                parsed = parse.urlparse(li.find("a")["href"])
                print(li_num, parse_qs(parsed.query)["blogId"], parse_qs(parsed.query)["logNo"])
                bloger_id = parse_qs(parsed.query)["blogId"]
                post_ids.append(parse_qs(parsed.query)["logNo"])

                total_post_cnt += 1
            post_ids.reverse()

            url = f"https://m.blog.naver.com/{bloger_id[0]}/"

            try:
                if os.path.exists(last_download_path):
                    self.fname = QFileDialog.getExistingDirectory(parent=self, caption="Save as", directory=last_download_path)
                    last_download_path = self.fname
                else:
                    last_download_path = "./"
                    self.fname = QFileDialog.getExistingDirectory(parent=self, caption="Save as", directory=last_download_path)
                    last_download_path = self.fname
            except PermissionError:
                print("Permission Error")
                self.return_signal = True
                self.close()
                self.mw.show()

            if ("/" in self.fname) is False:
                print("path error")
                self.return_signal = True
                self.close()
                self.mw.show()

            else:
                self.dir_loc = self.fname + "/" + category_title
                if os.path.exists(self.dir_loc) is False:
                    print(f"Make directory at {self.dir_loc}")
                    os.mkdir(f"{self.dir_loc}")

                failed_urls = list()
                per = len(post_ids) / 1000
                print(f"per: {per}")
                title_history = list()
                for post_num, post_id in enumerate(post_ids):
                    self.pbar.setFormat("%.1f %%" % (post_num / per / 10))
                    QApplication.processEvents()
                    self.pbar.setValue((post_num / per / 10))
                    dm = DownloadModule()
                    try:
                        post_title, img_urls, number_of_imgs = dm.blog_post_image_finder(url + post_id[0])
                    except Exception as e:
                        print(e)
                        if (url + post_id[0] in failed_urls) is False:
                            failed_urls.append(url + post_id[0])
                        continue
                    while (post_title in title_history) is True:
                        print(f"Duplicate file name. Changed {post_title} to {post_title}_")
                        post_title = post_title + "_"
                    title_history.append(post_title)

                    for special_character in special_characters:
                        post_title = post_title.replace(special_character, "")

                    print(f"{post_num + 1}/{total_post_cnt}번 째 포스트의 이미지들을 다운로드합니다.")
                    print("post title:", post_title)

                    if number_of_imgs == 0:
                        print(f"::ERROR:: Zero Image Error occured at {url + post_id[0]}")
                        if (url + post_id[0] in failed_urls) is False:
                            failed_urls.append(url + post_id[0])
                        continue

                    if self.img_combine_status is True:
                        imgs = list()
                        for img_url in img_urls:
                            org_name = parse.urlparse(img_url).path.split("/")[-1]
                            org_name, ext = os.path.splitext(org_name)
                            if ext == ".gif":
                                self.return_signal = True
                                print("gif can't be combined")
                                self.close()
                                self.mw.show()
                            img_url = parse.urlsplit(img_url)
                            img_url = img_url[0] + "://" + img_url[1] + parse.quote(img_url[2]) + "?" + img_url[3]
                            try:
                                img = Image.open(req.urlopen(img_url))
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(req.urlopen(img_url))
                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            imgs.append(np_img)
                        combined_img = CombineImage(imgs)
                        print(f"shape of combined_img: {np.shape(combined_img)}")
                        is_success, im_buf_arr = cv2.imencode(ext, combined_img)
                        if make_folder_status is True:
                            if number_of_imgs == 1:
                                if self.post_num_status is True:
                                    print(f"Image write at {self.dir_loc}/{post_num} {post_title}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}{ext}")
                                    continue
                                else:
                                    print(f"Image write at {self.dir_loc}/{post_title}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_title}{ext}")
                                    continue
                            if self.post_num_status is True:
                                if os.path.exists(f"{self.dir_loc}/{post_num} {post_title}") is False:
                                    os.mkdir(f"{self.dir_loc}/{post_num} {post_title}")
                                print(f"Image write at {self.dir_loc}/{post_num} {post_title}/{post_title}{ext}")
                                im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}/{post_title}{ext}")
                                continue
                            else:
                                if os.path.exists(f"{self.dir_loc}/{post_title}") is False:
                                    os.mkdir(f"{self.dir_loc}/{post_title}")
                                print(f"Image write at {self.dir_loc}/{post_title}/{post_title}{ext}")
                                im_buf_arr.tofile(f"{self.dir_loc}/{post_title}/{post_title}{ext}")
                                continue
                        elif make_folder_status is False:
                            if self.post_num_status is True:
                                print(f"Image write at {self.dir_loc}/{post_num} {post_title}{ext}")
                                im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}{ext}")
                                continue
                            else:
                                print(f"Image write at {self.dir_loc}/{post_title}{ext}")
                                im_buf_arr.tofile(f"{self.dir_loc}/{post_title}{ext}")
                                continue
                    elif self.img_combine_status is False:
                        for img_url_num, img_url in enumerate(img_urls):
                            splited_url_1 = img_url.rsplit("?", 1)
                            splited_url_1[1] = "?" + splited_url_1[1]
                            splited_url_2 = splited_url_1[0].rsplit("/", 1)
                            splited_url_2[1] = "/" + parse.quote(splited_url_2[1]) + splited_url_1[1]
                            img_url = splited_url_2[0] + splited_url_2[1]

                            org_name = parse.urlparse(img_url).path.split("/")[-1]
                            org_fname, ext = os.path.splitext(org_name)
                            print(f"img_url: {img_url}\timg_url_num: {img_url_num}")
                            if requests.get(img_url).status_code == 404:
                                print(f"::ERROR:: 404 Error occured at {url + post_id[0]}")
                                if (url + post_id[0] in failed_urls) is False:
                                    failed_urls.append(url + post_id[0])
                                continue
                            img_url = parse.urlsplit(img_url)
                            img_url = img_url[0] + "://" + img_url[1] + parse.quote(img_url[2]) + "?" + img_url[3]
                            try:
                                img = Image.open(req.urlopen(img_url))
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(req.urlopen(img_url))
                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            if ext == ".gif":
                                if make_folder_status is True:
                                    if number_of_imgs == 1:
                                        if self.post_num_status is True:
                                            print(f"Download file name: {self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                            req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                            continue
                                        else:
                                            print(f"Download file name: {self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                            req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                            continue
                                    if self.post_num_status is True:
                                        if os.path.exists(f"{self.dir_loc}/{post_num} {post_title}") is False:
                                            os.mkdir(f"{self.dir_loc}/{post_num} {post_title}")
                                        print(f"Download file name: {self.dir_loc}/{post_num} {post_title}/{post_title}_{img_url_num}{ext}")
                                        req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_num} {post_title}/{post_title}_{img_url_num}{ext}")
                                        continue
                                    elif self.post_num_status is False:
                                        if os.path.exists(f"{self.dir_loc}/{post_title}") is False:
                                            os.mkdir(f"{self.dir_loc}/{post_title}")
                                        print(f"Download file name: {self.dir_loc}/{post_title}/{post_title}_{img_url_num}{ext}")
                                        req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_title}/{post_title}_{img_url_num}{ext}")
                                        continue
                                elif make_folder_status is False:
                                    if self.post_num_status is True:
                                        print(f"Download file name: {self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                        req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                        continue
                                    else:
                                        print(f"Download file name: {self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                        req.urlretrieve(img_url, filename=f"{self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                        continue

                            try:
                                is_success, im_buf_arr = cv2.imencode(ext, np_img)
                            except:
                                if (url + post_id[0] in failed_urls) is False:
                                    failed_urls.append(url + post_id[0])
                                continue
                            if make_folder_status is True:
                                if number_of_imgs == 1:
                                    if self.post_num_status is True:
                                        print(f"Download file name: {self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                        im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                        continue
                                    else:
                                        print(f"Download file name: {self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                        im_buf_arr.tofile(f"{self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                        continue
                                if self.post_num_status is True:
                                    if os.path.exists(f"{self.dir_loc}/{post_num} {post_title}") is False:
                                        os.mkdir(f"{self.dir_loc}/{post_num} {post_title}")
                                    print(f"Download file name: {self.dir_loc}/{post_num} {post_title}/{post_title}_{img_url_num}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}/{post_title}_{img_url_num}{ext}")
                                    continue
                                else:
                                    if os.path.exists(f"{self.dir_loc}/{post_title}") is False:
                                        os.mkdir(f"{self.dir_loc}/{post_title}")
                                    print(f"Download file name: {self.dir_loc}/{post_title}/{post_title}_{img_url_num}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_title}/{post_title}_{img_url_num}{ext}")
                                    continue
                            elif make_folder_status is False:
                                if self.post_num_status is True:
                                    print(f"Download file name: {self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_num} {post_title}_{img_url_num}{ext}")
                                    continue
                                else:
                                    print(f"Download file name: {self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                    im_buf_arr.tofile(f"{self.dir_loc}/{post_title}_{img_url_num}{ext}")
                                    continue

                if len(failed_urls) > 0:
                    fhandler = open(f"{self.dir_loc}/failed_list.txt", 'a')
                    for failed_url_num, failed_url in enumerate(failed_urls):
                        print(f"failed_url {failed_url_num}: {failed_url}")
                        fhandler.write(failed_url + "\n")
                    fhandler.close()

                self.return_signal = True
                print("Done")

                self.ShowDirectory()
                self.mw.show()
                self.close()

    def ShowDirectory(self):
        reply = QMessageBox.question(self, "Message", "다운로드 한 파일이 있는\n디렉터리를 여시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            os.startfile(f"{self.dir_loc}")
        else:
            pass

    def closeEvent(self, QCloseEvent):
        if self.return_signal is False:
            quit()


class ShowPicWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedSize(960, 720)
        self.setWindowTitle("Showing pictures")

        self.layout = None
        self.scrollArea = None
        self.scrollAreaWidgetContents = None
        self.grid = None

        self.combine_status = QCheckBox("Combine Images", self)

        self.checkbutton_loc = list()
        self.fname = None

        self.raw_datas = list()
        self.selected_numbers = list()

        self.mw = MainWindow()

        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)
        self.scrollArea = QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaWidgetContents = QWidget()
        self.grid = QGridLayout(self.scrollAreaWidgetContents)
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.layout.addWidget(self.scrollArea)

        row_count = 0
        column_count = 0

        for img_url_num, url in enumerate(img_urls):
            if column_count == 6:
                row_count += 2
                column_count = 0
            lbl = QLabel()

            url = parse.urlsplit(url)
            url = url[0] + "://" + url[1] + parse.quote(url[2]) + "?" + url[3]
            if requests.get(url).status_code == 404:
                print(f"::ERROR:: Not Found: {url}")
                continue
            raw_data = req.urlopen(url).read()
            self.raw_datas.append(req.urlopen(url))
            pixmap = QPixmap()
            pixmap.loadFromData(raw_data)

            width = pixmap.width()
            height = pixmap.height()

            new_width, new_height = image_resize(width, height, 125)

            print(f"pixmap.size(): {pixmap.size()}")
            print(f"new_width: {new_width}\nnew_height: {new_height}\n")

            pixmap = pixmap.scaled(new_width, new_height)
            lbl.setPixmap(pixmap)
            self.grid.addWidget(lbl, row_count, column_count)

            checkbutton = QCheckBox(f"img_{img_url_num}\nshape: {width, height}", self)
            checkbutton.toggle()
            self.grid.addWidget(checkbutton, row_count + 1, column_count)
            self.checkbutton_loc.append((row_count + 1, column_count, img_url_num))
            self.selected_numbers.append(img_url_num)

            column_count += 1

        select_done_btn = QPushButton("Done", self)
        select_done_btn.clicked.connect(self.SelectDoneButtonMethod)
        self.layout.addWidget(select_done_btn)

        cancel_btn = QPushButton("Cancel", self)
        cancel_btn.clicked.connect(self.CancelButtonMethod)
        self.layout.addWidget(cancel_btn)

        self.layout.addWidget(self.combine_status)

    def SelectDoneButtonMethod(self):
        global post_title
        global last_download_path

        print(self.checkbutton_loc)
        selected_urls = list()
        for locs in self.checkbutton_loc:
            locs_0, locs_1 = locs[0], locs[1]
            item = self.grid.itemAtPosition(locs_0, locs_1)
            widget = item.widget()
            print(widget.isChecked())
            if widget.isChecked() is True:
                selected_urls.append(img_urls[locs[2]])
        print(selected_urls)
        print(len(selected_urls))

        try:
            if os.path.exists(last_download_path):
                self.fname = QFileDialog.getExistingDirectory(parent=self, caption="Save as", directory=last_download_path)
                last_download_path = self.fname
            else:
                last_download_path = "./"
                self.fname = QFileDialog.getExistingDirectory(parent=self, caption="Save as", directory=last_download_path)
                last_download_path = self.fname
            print(f"self.fname: {self.fname}")
            if ("/" in self.fname) is False:
                print("path error")
                self.close()
                self.mw.show()
            else:
                if make_folder_status is True:
                    if os.path.exists(f"{self.fname}/{post_title}") is False:
                        print(f"Make directory at {self.fname}/{post_title}")
                        os.mkdir(f"{self.fname}/{post_title}")
                    else:
                        while os.path.exists(f"{self.fname}/{post_title}"):
                            post_title = post_title + "_"
                        print(f"Make directory at {self.fname}/{post_title}")
                        os.mkdir(f"{self.fname}/{post_title}")
                    if self.combine_status.isChecked() is True:
                        imgs = list()
                        for selected_url in selected_urls:
                            org_name = parse.urlparse(selected_url).path.split("/")[-1]
                            org_name, ext = os.path.splitext(org_name)
                            selected_url = parse.urlsplit(selected_url)
                            selected_url = selected_url[0] + "://" + selected_url[1] + parse.quote(selected_url[2]) + "?" + selected_url[3]
                            try:
                                img = Image.open(req.urlopen(selected_url))
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(req.urlopen(selected_url))

                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            imgs.append(np_img)
                        combined_img = CombineImage(imgs)
                        print(f"shape of combined_img: {np.shape(combined_img)}")
                        print(f"Image write at {self.fname}/{post_title}/{post_title}{ext}")
                        is_success, im_buf_arr = cv2.imencode(ext, combined_img)
                        im_buf_arr.tofile(f"{self.fname}/{post_title}/{post_title}{ext}")
                    elif self.combine_status.isChecked() is False:
                        for selected_url_num, selected_url in enumerate(selected_urls):
                            org_name = parse.urlparse(selected_url).path.split("/")[-1]
                            org_fname, ext = os.path.splitext(org_name)
                            print(selected_url)
                            print(f"Download file name: {self.fname}/{post_title}/{post_title}_{selected_url_num}{ext}")
                            try:
                                img = Image.open(self.raw_datas[self.selected_numbers[selected_url_num]])
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(self.raw_datas[self.selected_numbers[selected_url_num]])

                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            print(f"shape of np_img: {np.shape(np_img)}")
                            if ext == ".gif":
                                req.urlretrieve(selected_url, filename=f"{self.fname}/{post_title}/{post_title}_{selected_url_num}{ext}")
                                continue
                            is_success, im_buf_arr = cv2.imencode(ext, np_img)
                            im_buf_arr.tofile(f"{self.fname}/{post_title}/{post_title}_{selected_url_num}{ext}")

                    self.ShowDirectory(True)
                elif make_folder_status is False:
                    if self.combine_status.isChecked() is True:
                        imgs = list()
                        for selected_url in selected_urls:
                            org_name = parse.urlparse(selected_url).path.split("/")[-1]
                            org_name, ext = os.path.splitext(org_name)
                            selected_url = parse.urlsplit(selected_url)
                            selected_url = selected_url[0] + "://" + selected_url[1] + parse.quote(selected_url[2]) + "?" + selected_url[3]
                            try:
                                img = Image.open(req.urlopen(selected_url))
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(req.urlopen(selected_url))

                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            imgs.append(np_img)
                        combined_img = CombineImage(imgs)
                        while os.path.exists(f"{self.fname}/{post_title}{ext}"):
                            post_title = post_title + "_"
                        print(f"shape of combined_img: {np.shape(combined_img)}")
                        print(f"Image write at {self.fname}/{post_title}{ext}")
                        is_success, im_buf_arr = cv2.imencode(ext, combined_img)
                        im_buf_arr.tofile(f"{self.fname}/{post_title}{ext}")
                    elif self.combine_status.isChecked() is False:
                        dup_status = True
                        for selected_url_num, selected_url in enumerate(selected_urls):
                            org_name = parse.urlparse(selected_url).path.split("/")[-1]
                            org_fname, ext = os.path.splitext(org_name)
                            while dup_status is True:
                                dup_status = False
                                for dup_check_num in range(len(selected_urls)):
                                    tmp_title = f"{self.fname}/{post_title}_{dup_check_num}{ext}"
                                    if os.path.exists(tmp_title):
                                        dup_status = True
                                        post_title = post_title + "_"
                                        break
                            print(f"Download file name: {self.fname}/{post_title}_{selected_url_num}{ext}")
                            try:
                                img = Image.open(self.raw_datas[self.selected_numbers[selected_url_num]])
                            except ConnectionResetError:
                                print("Connection reset error occured. Wait a moment...")
                                time.sleep(2)
                                img = Image.open(self.raw_datas[self.selected_numbers[selected_url_num]])
                            np_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                            print(f"shape of np_img: {np.shape(np_img)}")
                            if ext == ".gif":
                                req.urlretrieve(selected_url, filename=f"{self.fname}/{post_title}_{selected_url_num}{ext}")
                                continue
                            is_success, im_buf_arr = cv2.imencode(ext, np_img)
                            im_buf_arr.tofile(f"{self.fname}/{post_title}_{selected_url_num}{ext}")

                    self.ShowDirectory(new_dir=False)
                print("Done")
                self.close()
                self.mw.show()

        except PermissionError:
            self.close()
            self.mw.show()

    def CancelButtonMethod(self):
        self.close()

    def ShowDirectory(self, new_dir: bool):
        reply = QMessageBox.question(self, "Message", "다운로드 한 파일이 있는\n디렉터리를 여시겠습니까?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if new_dir is True:
            if reply == QMessageBox.Yes:
                os.startfile(f"{self.fname}/{post_title}/")
            else:
                pass
        else:
            if reply == QMessageBox.Yes:
                os.startfile(self.fname)
            else:
                pass

    def closeEvent(self, QCloseEvent):
        self.mw.show()


class ErrorPage(QWidget):
    def __init__(self, code):
        super().__init__()
        self.mw = MainWindow()

        if code == "WINDOW_NOT_EXIST":
            self.WindowNotExist()
        elif code == "NO_IMAGE":
            self.NoImage()
        elif code == "URLError":
            self.URLError()

    def WindowNotExist(self):
        grid = QGridLayout()
        self.setLayout(grid)
        self.setWindowTitle("Window Not Exist")

        label = QLabel("Window doesn't exist!")
        label.setAlignment(Qt.AlignCenter)

        font = label.font()
        font.setPointSize(25)
        font.setBold(True)

        label.setFont(font)

        grid.addWidget(label, 0, 0)

        return_btn = QPushButton("Return", self)
        return_btn.clicked.connect(self.ReturnBtnMethod)
        grid.addWidget(return_btn, 1, 0)

    def NoImage(self):
        self.setWindowTitle("No Image")
        grid = QGridLayout()
        self.setLayout(grid)

        label = QLabel("Can't Find Image!")
        label.setAlignment(Qt.AlignCenter)

        font = label.font()
        font.setPointSize(25)
        font.setBold(True)

        label.setFont(font)

        grid.addWidget(label, 0, 0)

        return_btn = QPushButton("Return", self)
        return_btn.clicked.connect(self.ReturnBtnMethod)
        grid.addWidget(return_btn, 1, 0)

    def URLError(self):
        self.setWindowTitle("URL Error")
        grid = QGridLayout()
        self.setLayout(grid)

        label = QLabel("URL Error!\nPlease Checking URL")
        label.setAlignment(Qt.AlignCenter)

        font = label.font()
        font.setPointSize(25)
        font.setBold(True)

        label.setFont(font)

        grid.addWidget(label, 0, 0)

        return_btn = QPushButton("Return", self)
        return_btn.clicked.connect(self.ReturnBtnMethod)
        grid.addWidget(return_btn, 1, 0)

    def ReturnBtnMethod(self):
        self.close()
        self.mw.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec_()
