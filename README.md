# Naver Blog Image Downloader

## 설명

### 경고

- "chromedriver.exe"는 항상 "Blog Image Downloader.py" 혹은 "Blog Image Downloader.exe"와 같은 폴더에 있어야 합니다.
- 프로그램이 예상치 않게 종료되기 전까지는 에러가 발생한 것이 아니므로 잠시만 기다리시면 작업이 진행됩니다.
- 다운로드 할 파일의 이름이 중복된다면, 중복 문제가 해결될 때까지 파일의 이름 뒤에 "_"가 추가됩니다.

### 실행방법

#### 포스트 다운로드 시

1. "Blog Image Downloader.py" 혹은 "Blog Image Downloader.exe"를 실행시켜주세요.
2. 네이버 블로그 포스트의 URL을 복사하여 "Post URL: "에 붙여넣기 해주세요.
    1. "Make Folder" 체크박스를 체크하시면 이미지는 "포스트 제목/포스트 제목_이미지 넘버.해당 파일 확장자"에 저장됩니다.
3. "Done" 버튼을 클릭하시고 잠시만 기다려주세요.
4. 블로그 포스트의 이미지들이 새로운 창에 뜰 것입니다. 이미지의 설명을 보시고 다운로드 하실 이미지들을 선택해주세요.<br>
   "Combine Image" 체크박스를 체크하시면 포스트의 이미지들은 세로로 길게 하나의 파일로 합쳐져서 저장됩니다.
5. "Done" 버튼을 클릭하시고 선택하신 이미지들을 저장할 경로를 선택해주세요.
6. 선택된 이미지들이 지정된 경로에 저장됩니다. 다운로드 작업이 끝날때까지 잠시만 기다려주세요.

#### 카테고리 다운로드 시

1. "Blog Image Downloader.py" 혹은 "Blog Image Downloader.exe"를 실행시켜주세요.
2. "Category" 버튼을 클릭해주세요.
3. 네이버 블로그의 카테고리 URL을 복사하여 "Category URL: "에 붙여넣기 해주세요.
    1. "Make Folder" 체크박스를 체크하시면 이미지는 "카테고리 제목/포스트 제목/포스트 제목_이미지 넘버.해당 파일 확장자"에 저장됩니다.
    2. "Make Folder" 체크박스를 해제하시면 이미지는 "카테고리 제목/포스트 제목_이미지 넘버.해당 파일의 확장자"에 저장됩니다.
    3. "Combine posts images" 체크박스를 체크하시면 각 포스트의 이미지들은 세로로 길게 하나의 파일로 합쳐져서 저장됩니다.
    4. "Add post number" 체크박스를 체크하시면 포스트들의 번호가 각 폴더("Make Folder" 체크박스를 체크한 경우) 혹은 각 파일("Make Folder" 체크박스를 해제한 경우)의 이름
       앞에 추가됩니다.
4. "Done" 버튼을 클릭하시고 잠시만 기다려주세요. 이 작업은 몇 초, 혹은 몇 분이 소요됩니다.
5. 포스트들의 이미지를 저장할 경로를 선택해주세요.
6. 다운로드가 시작됩니다. 잠시만 기다려주세요.

## Description

### WARNING

- "chromedriver.exe" should always in the same directory as "Blog Image Downloader.py" or "Blog Image Downloader.exe"
- The error did not occur until the program exits unexpectedly.
- If the file name is duplicated, "_" is added until there is no duplicate.

### How can I run it?

#### In case of Post Download

1. Running "Blog Image Downloader.py" or "Blog Image Downloader.exe"
2. Copying URL from Naver Blog post and paste URL at "Post URL: "
    1. If you checked the "Make Folder" checkbox, images will be downloaded "POST TITLE/POST TITLE_IMAGE NUMBER.FILE
       EXTENTION"
3. Push the "Done" button and wait a moment.
4. Blog Post's images will be shown at a new window. Select images description of what you want to download.
    1. If you checked the "Combine Images" checkbox, Post's images will be vertically combined in one file.
5. Push the "Done" button and select the path where you want to download selected images.
6. Now, the selected images are downloaded to the specified path. Wait a while for the download operation to complete.

#### In case of Category Download

1. Running "Blog Image Downloader.py" or "Blog Image Downloader.exe"
2. Select the "Category" radio button.
3. Copying URL from Naver Blog Category and paste URL at "Category URL: "
    1. If you checked the "Make Folder" checkbox, Images will be downloaded "CATEGORY TITLE/POST TITLE/POST TITLE_IMAGE
       NUMBER.FILE EXTENTION"
    2. If you unchecked the Make Folder checkbox, Images will be downloaded "CATEGORY TITLE/POST TITLE_IMAGE NUMBER.FILE
       EXTENTION"
    3. If you checked the "Combine posts images" checkbox, each Post's images will be vertically combined in one file.
    4. If you checked the "Add post number" checkbox, Post's numbers will be prepended at each Folder(If you checked
       the "Make Folder" checkbox) or each File(If you unchecked the "Make Folder" checkbox).
4. Push the "Done" button and wait a moment. It will take a few seconds or minutes.
5. Select the path where you want to download posts images.
6. The download will be started. Please wait a few minutes.

## Used Libraries

### Parsing

~~~~
1. BeautifulSoup
2. urllib.request
3. urllib.parse
4. selenium
5. requests
~~~~

### Image Processing

~~~~
1. PIL
2. cv2
3. numpy
~~~~

### GUI

~~~~
1. PyQt5.QtWidgets
2. PyQt5.QtCore
3. PyQt5.QtGui
~~~~

### Others

~~~~
1. os
2. sys
~~~~
