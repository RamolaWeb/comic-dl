#!/usr/bin/env python
# -*- coding: utf-8 -*-

import globalFunctions
import re
import sys
import os
import logging


class FoolSlide(object):
    def __init__(self, manga_url, **kwargs):

        current_directory = kwargs.get("current_directory")
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")

        self.manga_name = self.name_cleaner(manga_url)

        if "/reader/series/" in manga_url:
            self.full_manga(manga_url=manga_url, comic_name=self.manga_name, sorting=self.sorting)
        elif "/reader/read/" in manga_url:
            self.single_chapter(manga_url, self.manga_name)


    def single_chapter(self, chapter_url, comic_name, **kwargs):

        chapter_number = str(chapter_url).split("/")[8].strip()

        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_url)
        img_links = self.image_links(source)
        logging.debug("Img Links : %s" % img_links)

        file_directory = str(comic_name) + '/' + "Chapter " + str(chapter_number) + "/"

        directory_path = os.path.realpath(file_directory)

        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        globalFunctions.GlobalFunctions().info_printer(comic_name, chapter_number)

        for link in img_links:
            link = link.replace("\\", "")
            file_name = "0" + str(link).split("/")[-1].strip()
            globalFunctions.GlobalFunctions().downloader(link, file_name, chapter_url, directory_path, log_flag=self.logging)

        return 0

    def image_links(self, source_code):

        try:
            source_dict = re.search(r"\= \[(.*?)\]\;", str(source_code)).group(1)

            image_links = re.findall(r"\"url\"\:\"(.*?)\"", str(source_dict))
            # file_names = re.findall(r"\"filename\"\:\"(.*?)\"", str(source_dict))

        except Exception as ImageLinksNotFound:
            print("Links : %s" % ImageLinksNotFound)
            sys.exit()

        return image_links

    def name_cleaner(self, url):
        initial_name = str(url).split("/")[5].strip()
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        anime_name = str(safe_name.title()).replace("-", " ")

        return anime_name

    def full_manga(self, manga_url, comic_name, sorting, **kwargs):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=manga_url)
        # print(source)
        chapter_text = source.findAll('div', {'class': 'title'})
        all_links = []

        for link in chapter_text:
            x = link.findAll('a')
            for a in x:
                url = a['href']
                all_links.append(url)
        logging.debug("All Links : %s" % all_links)

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in all_links:
                self.single_chapter(chapter_url=chap_link, comic_name=comic_name)
        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            # print("Running this")
            for chap_link in all_links[::-1]:
                self.single_chapter(chapter_url=chap_link, comic_name=comic_name)

        print("Finished Downloading")
        return 0
