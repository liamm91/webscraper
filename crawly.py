#!/usr/bin/python3
# -*- coding: utf_8 -*-

__author__ = "Liam Major"
__version__ = "1.6"

'''
#Made by Liam Major
#Version 1.6
#Last Updated 2/9/2018 -> 1.6
#pip install BeautifulSoup4
'''

from bs4 import BeautifulSoup  # used to parse through html links
import time  # used for logging / time stamps
# used for getting html requests from web pages / used for debugging links
import urllib.request
import uuid  # makes use of uuid.uuid4() for unique names for crawler threads
import threading  # used to thread the parsing of each link to improve speed
import socket  # used for debugging links
import sqlite3  # used to store links

"""SQL Variables"""
sql_lock = threading.Lock()
sql_filter = []
table_qry = """CREATE TABLE IF NOT EXISTS bank_%s (id integer primary key, child text, parent text);"""
insert_qry = """INSERT INTO bank_%s VALUES (%d, "%s", "%s");"""
db = sqlite3.connect("data_bank.db", 1, check_same_thread=False)
db_cur = db.cursor()


"""Variables"""
id_ = 1  # used as a constraint to limit threads
banned_sites = []  # used to stop unneeded traffic
exceptions = {"youtu.be": "youtube", "goo.gl": "google"}


def setup():  # setup for the function if the __name__ == __main__
    while True:
        link = str(
            input("$ Please enter a link to a website\n$ Ex. https://www.youtube.com\n$ "))
        try:
            with urllib.request.urlopen(link) as response:  # testing link
                if response:
                    print("$ good link")
                    del response
                    break
                else:
                    print("$ bad link try again")
                    continue
        except Exception:
            print("$ bad link try again")

    root = link.split('.')[1]

    while True:
        try:
            tries = int(input("$ How many tries? *0 for forever*\n$ "))
            if tries == 0:
                tries = False
            else:
                pass
            break
        except Exception:
            print("$ bad number try again")
            continue

    while True:
        verbose = str(input("$ Screen output (aka verbose)? (Y/N)\n$ "))
        if verbose[0] in "yY":
            verbose = True
            break
        elif verbose[0] in 'nN':
            verbose = False
            break
        else:
            print("$ bad choice try again")
            continue

    return link, root, tries, verbose


class link_crawler(object):
    site_endings = [".com", ".ca", ".org", ".edu",
                    ".gov", ".net", ".io", ".us", ".ru", ".gg"]

    '''grabs links from a website and chains off of them'''

    def __init__(self, url="", name="main", tries=100, verbose=False, parent="start"):
        """Making all vars"""
        global id_  # setting id to limit threads
        self.id = id_
        id_ += 1

        self.name = str(name)
        self.parent = parent
        self.link = url
        self.verbose = verbose
        self.root = self.link.split('.')[1]
        self.try_count = tries

        """Checking all vars"""
        if not url:
            # self.link -> the url passed to the crawler to parse
            raise TypeError("need a url to process")

        if not isinstance(tries, bool) and not isinstance(tries, int):
            raise TypeError("tries must be a bool or int not %s" % type(tries))

        if not isinstance(verbose, bool):
            raise TypeError("kwarg verbose is not bool but %s" % type(verbose))

        # checking if the url is an exception to prevent any abnormalities
        for key in exceptions.keys():
            if key in self.link:
                self.root = exceptions[key]

        if self.root.split('/')[0] in self.site_endings or '/' in self.root:
            self.root = self.link[:self.link.index('.')].split("//")[1]

        """Activates if all vars are checked"""
        if self.id < self.try_count or not self.try_count:
            # deciding if the id is less than try count or try_count is false (override), else it will stop
            self.upper_body()

        else:
            if self.verbose:
                print("%s stopped due to start conditions being false" % self.name)

            del self

    def _write_to_log(self, msg, err_log=False, proc_when_caught=""):
        '''method to write to log to save lines'''

        if err_log:  # if err_log is true it will write to an error log
            if self.verbose:
                print("%s | %s error: %s" % (self.name, proc_when_caught, msg))
            try:
                with open("crawl_err_log_%s.txt" % root, "a") as file_out:
                    file_out.write(
                        "%s | %s err caught: %r;\n" % (time.ctime(), self.name, msg))
                    file_out.flush()
                    file_out.close()
            except Exception as error:
                if self.verbose:
                    print("%s error with writing to log: %r" %
                          (self.name, error))

        else:  # else it will write to a normal log
            try:
                with open("crawl_log_%s.txt" % root, "a") as file_out:
                    file_out.write("%s | %s\n" % (time.ctime(), msg))
                    file_out.flush()
                    file_out.close()
            except Exception as error:
                if self.verbose:
                    print("%s error with writing to log: %s" %
                          (self.name, error))
                del error

    def tag_parser(self, contents):
        """algorithm to sort, correct or make html links **not 100% perfect**"""

        if self.verbose:
            print("%s scanning for tags" % self.name)

        a_tags = []
        end = None

        for link in contents.find_all('a'):
            href = str(link.get("href"))
            if href:
                try:
                    if "http" in href:  # if "http" is in the link it will try and get an html response else
                        try:  # else it will raise an error to go to the rest of the algorithm
                            with urllib.request.urlopen(href) as response:
                                if response:
                                    del response
                                    if href not in a_tags:
                                        a_tags.append(href)

                                else:
                                    del response
                                    raise socket.gaierror

                        except Exception as e:
                            self._write_to_log(
                                e, err_log=True, proc_when_caught="during tag scanning")

                            # filtering out the redirect cause it causes errors
                            if "redirect" in str(e):
                                pass
                            elif "HTTPError 429" in str(e):
                                banned_sites.append(self.root)

                            raise socket.gaierror

                    else:  # it will try and get the addr info, to see if it is a valid link
                        try:  # if yes it will try and make it into a proper url, else it will raise an error
                            temp = socket.getaddrinfo(
                                href, 80, proto=socket.IPPROTO_TCP)
                            if temp:
                                del temp
                                if "https" in self.link:
                                    http_type = "https"
                                else:
                                    http_type = "http"
                                temp_link = http_type + href

                                if temp_link not in temp_link:
                                    a_tags.append(temp_link)
                                    del temp_link
                                else:
                                    pass

                        except UnicodeError:
                            raise socket.gaierror

                except socket.gaierror:
                    if href[0] == '/':  # meaning this is the home page of the website
                        temp_link = self.link
                        if temp_link[-1] == '/':
                            temp_link = temp_link[:-1]

                        if temp_link not in a_tags:
                            a_tags.append(temp_link)
                            del temp_link, href
                        else:
                            pass

                    # this will make it a url to a website by
                    elif href[0] == '/' and href[1] == '/':
                        if "https" in link:  # by pairing it with http: / https: and test it
                            temp_link = "https:" + href
                        else:
                            temp_link = "http:" + href

                        try:
                            with urllib.request.urlopen(temp_link) as response:
                                if response:
                                    if temp_link not in a_tags:
                                        a_tags.append(temp_link)
                                    else:
                                        pass
                                else:
                                    del response
                        except:
                            del temp_link, href
                            pass

                    else:  # trying to get the ending of the link, else it will be .com
                        if not end:
                            for ending in self.site_endings:
                                if ending in link:
                                    break
                                else:
                                    pass
                            if not end:
                                end = ".com"

                        if "https" in link:  # solving wether it is a https or http
                            http_type = "https://"
                        else:
                            http_type = "http://"

                        if href:  # adding to a list to return
                            temp_link = http_type + href + end
                            if temp_link.count("http") >= 2:
                                temp_link = temp_link[temp_link.index(
                                    "//") + 2:]

                            if temp_link.split('/')[-1].split('.')[-1] in self.site_endings:
                                temp = ''
                                for item in temp_link.split('.'):
                                    if item not in self.site_endings:
                                        temp += str(item)
                                    else:
                                        pass
                                temp_link = temp
                                del temp

                            if "None" not in temp_link and temp_link not in a_tags:
                                a_tags.append(temp_link)
                                del temp_link
                            else:
                                pass
            else:
                pass

        if self.verbose and a_tags:
            print("href collected %s" % str(a_tags))

        return a_tags  # returning the list of links

    def write_url_to_bank(self):
        '''writing to a bank of urls the crawler has collected'''
        if self.verbose:
            print("%s writing to link bank: bank_%s" % (self.name, self.root))

        if self.link not in sql_filter:
            try:
                sql_lock.acquire()
                sql_filter.append(self.link)

                db_cur.execute(table_qry % self.root)

                #print(insert_qry % (root, self.id, self.link))
                db_cur.execute(insert_qry %
                               (self.root, self.id, self.link, self.parent))
                self._write_to_log("wrote to bank link: %s" % self.link)

            except sqlite3.Error as error:
                self._write_to_log(str(error) + " %s" % self.link,
                                   err_log=True, proc_when_caught="writing to bank")
                db.rollback()

            finally:
                db.commit()
                sql_lock.release()

            return True

        else:
            print("%s is already in bank_%s" % (self.name, self.root))
            return False

    def upper_body(self):
        '''main loop called in the __init__ method to scrape the webpage of urls and,
            feeding each url to another crawler'''

        try:
            if self.verbose:
                print("%s trying to open link %s" % (self.name, self.link))

            if self.root not in banned_sites:
                with urllib.request.urlopen(self.link) as response:
                    # trying to open and parse the contents with BeautifulSoup
                    self.contents = BeautifulSoup(
                        response.read(), "html.parser")
                    response.close()

                    if self.contents and self.verbose:
                        print("%s link opened %s" % (self.name, self.link))
                        self._write_to_log(
                            "%s | success opening page: %s" % (self.name, self.link))

                    elif not self.contents and self.verbose:
                        print("%s link failed to open link %s" %
                              (self.name, self.link))

                    else:
                        return False

                    temp_rcode = self.write_url_to_bank()
                    del response

                # testing the return value of the bank writing
                if temp_rcode:
                    del temp_rcode

                    # there is no need to scrape a banked page
                    self.tags = self.tag_parser(self.contents)

                    # parsing the contents of the page of pass to the link parsing algorithm
                    if self.tags:  # if there are links in self.tags make new crawlers
                        self.spawn_crawlers()

                    else:
                        self._write_to_log("tried to scrape banked url")
                        return False

                    # returning the crawler as true if the job is completed
                    return True

                else:
                    return False

            else:
                self._write_to_log("tried to accessed banned site")
                del self
                return False

        except Exception as error:
            """writing error to log and gathering other info"""
            self._write_to_log(error, err_log=True,
                               proc_when_caught="during loop")

            # denied http request filtering
            if "HTTPError 429" in str(error):
                banned_sites.append(self.root)

            del self, error
            return False

    def spawn_crawlers(self):
        """creating new threads to parse through websites"""
        t_list = []

        for branch in self.tags:  # making new threaded web crawlers
            t = threading.Thread(target=link_crawler, kwargs=({"url": branch, "tries": self.try_count,
                                                               "name": uuid.uuid4(), "verbose": self.verbose,
                                                               "parent": self.link}))
            t.start()
            t_list.append(t)

        # joining the threads to stop then delete them to save memory
        for thread in t_list:
            if thread:
                thread.join()
                del thread

    def __str__(self):
        return "crawler object with name: %s with link: %s" % (self.name, self.link)


if __name__ == '__main__':
    link, root, tries, verbose = setup()
    link_crawler(url=link, name="main", tries=tries, verbose=verbose)
