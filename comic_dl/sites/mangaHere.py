#!/usr/bin/env python
# -*- coding: utf-8 -*-

import globalFunctions
import re
import os
import logging


class MangaHere(object):
    def __init__(self, manga_url, **kwargs):

        current_directory = kwargs.get("current_directory")
        self.logging = kwargs.get("log_flag")
        self.sorting = kwargs.get("sorting_order")
        self.comic_name = self.name_cleaner(manga_url)

        url_split = str(manga_url).split("/")

        if len(url_split) is 6:
            self.full_series(comic_url=manga_url, comic_name=self.comic_name, sorting=self.sorting)
        else:
            self.single_chapter(manga_url, self.comic_name)

    def single_chapter(self, comic_url, comic_name):
        # Some chapters have integer values and some have decimal values. We will look for decimal first.
        try:
            chapter_number = re.search(r"c(\d+\.\d+)", str(comic_url)).group(1)
        except:
            chapter_number = re.search(r"c(\d+)", str(comic_url)).group(1)

        source, cookies_main = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)
        last_page_number = str(re.search(r'total_pages\ \=\ (.*?) \;', str(source)).group(1)).strip()

        file_directory = str(comic_name) + '/' + str(chapter_number) + "/"

        directory_path = os.path.realpath(file_directory)

        globalFunctions.GlobalFunctions().info_printer(comic_name, chapter_number)

        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        for chapCount in range(1, int(last_page_number) + 1):

            chapter_url = str(comic_url) + '/%s.html' % chapCount
            logging.debug("Chapter Url : %s" % chapter_url)

            source_new, cookies_new = globalFunctions.GlobalFunctions().page_downloader(manga_url=chapter_url,
                                                                                        cookies=cookies_main)

            image_link_finder = source_new.findAll('section', {'class': 'read_img'})
            for link in image_link_finder:
                x = link.findAll('img')
                for a in x:
                    image_link = a['src']

                    if image_link in ['http://www.mangahere.co/media/images/loading.gif']:
                        pass
                    else:
                        file_name = "0" + str(chapCount) + ".jpg"
                        logging.debug("Image Link : %s" % image_link)
                        globalFunctions.GlobalFunctions().downloader(image_link, file_name, chapter_url, directory_path, log_flag=self.logging)

        return 0

    def name_cleaner(self, url):
        initial_name = str(url).split("/")[4].strip()
        safe_name = re.sub(r"[0-9][a-z][A-Z]\ ", "", str(initial_name))
        anime_name = str(safe_name.title()).replace("_", " ")

        return anime_name

    def full_series(self, comic_url, comic_name, sorting, **kwargs):
        source, cookies = globalFunctions.GlobalFunctions().page_downloader(manga_url=comic_url)

        all_links = re.findall(r"class=\"color_0077\" href=\"(.*?)\"", str(source))

        chapter_links = []

        for link in all_links:
            if 'mangahere.co/manga/' in link:
                chapter_links.append(link)
            else:
                pass

        logging.debug("All Links : %s" % all_links)

        if str(sorting).lower() in ['new', 'desc', 'descending', 'latest']:
            for chap_link in chapter_links:
                self.single_chapter(comic_url=str(chap_link), comic_name=comic_name)

        elif str(sorting).lower() in ['old', 'asc', 'ascending', 'oldest', 'a']:
            for chap_link in chapter_links[::-1]:
                self.single_chapter(comic_url=str(chap_link), comic_name=comic_name)

        print("Finished Downloading")
        return 0
