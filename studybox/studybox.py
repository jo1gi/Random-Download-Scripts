import requests
from dataclasses import dataclass
from typing import List, Any
import os
import rich

book_id = "<INSERT BOOKID HERE>"
authentiaction_token = "<INSERT AUTHENTICATIONTOKEN COOKIE HERE>"

@dataclass
class Chapter:
    title: str
    id: int
    sub_chapters: List[Any]

@dataclass
class Book:
    title: str
    id: str
    chapters: List[Chapter]

cookies = {
    "AuthenticationToken": authentiaction_token,
}

def get_chapters(data) -> List[Chapter]:
    result = []
    for chapter in data:
        result.append(
            Chapter(
                title = chapter["title"],
                id = chapter["uid"],
                sub_chapters = get_chapters(chapter["children"]),
            )
        )
    return result

def get_book_metadata(bookid: str) -> Book:
    resp = requests.get(f"https://{bookid}.ibog.studybox.dk/api/?type=834").json()
    book = Book(
        title = resp["site"]["metadata"]["title"],
        id = bookid,
        chapters = get_chapters(resp["navigation"][0]["children"]),
    )
    return book

def download_chapter(bookid: str, chapter: Chapter):
    return requests.get(
        f"https://{bookid}.ibog.studybox.dk/api/?id={chapter.id}",
        cookies = cookies
    ).json()

def chapter_to_html(bookid: str, chapter: Chapter, level: int) -> str:
    result = ""
    result += f"<h{level}>{chapter.title}</h{level}>"
    chapter_info = download_chapter(bookid, chapter)
    try:
        for i in chapter_info["content"]["colPos0"]:
            if "bodytext" in i["content"]:
                result += i["content"]["bodytext"]
    except:
        print("Something went wrong")
        rich.print(chapter_info)
        exit()
    for sub_chapter in chapter.sub_chapters:
        result += chapter_to_html(bookid, sub_chapter, level+1)
    return result

def create_book_files(book: Book):
    if not os.path.exists(book.title):
        os.mkdir(book.title)
    for n, chapter in enumerate(book.chapters):
        print(f"Downloading chapter {n}")
        path = f"{book.title}/chapter_{n}.html"
        if os.path.exists(path):
            print("Skipping")
            continue
        html = chapter_to_html(book.id, chapter, 1)
        with open(path, "w") as f:
            f.write(html)

book = get_book_metadata(book_id)
create_book_files(book)
