#!/usr/bin/env python
import argparse
import sys
import os
import _init_paths
import imagedownloader
import pref_utils

if __name__ == '__main__':
    p = argparse.ArgumentParser(description='Help the user to download, crop, and handle images from ImageNet')
    p.add_argument('--wnid', nargs='+', help='ImageNet Wnid. E.g. : n02710324')
    p.add_argument('--destDir', nargs=1, help='the name of destination folder where synset(s) is stored. E.g. : ./download')
    p.add_argument('--file', nargs=1, help='name of file contains wnids. E.g. : ./wnids/all_wnids.txt')
    p.add_argument('--wnids', help='enable to download multiple wnids from a file that contains wnids', action='store_true', default=False)
    p.add_argument('--downloadImages', help='Should download images', action='store_true', default=False)
    p.add_argument('--downloadOriginalImages', help='Should download original images', action='store_true', default=False)
    p.add_argument('--downloadBoundingBox', help='Should download bouding box annotation files', action='store_true', default=False)
    # p.add_argument('--jobs', '-j', type=int, default=1, help='Number of parallel threads to download')
    # p.add_argument('--timeout', '-t', type=int, default=10, help='Timeout per image in seconds')
    # p.add_argument('--retry', '-r', type=int, default=10, help='Max count of retry for each image')
    p.add_argument('--verbose', '-v', action='store_true', help='Enable verbose log')
    if (len(sys.argv) < 2):
        print """\
        You gave me too few arguments.
        Usage:  ./downloadutilsTest03.py --downloadOriginalImages --wnids --file ./wnids/test-wnids.txt --destDir ./test
        """
        sys.exit(0)
    args = p.parse_args()
    print args.file[0]
    if args.wnid and wnIDs is None:
        print 'No wnid'
        sys.exit()

    downloader = imagedownloader.ImageNetDownloader()
    username = None
    accessKey = None
    destDir = args.destDir[0]
    if not os.path.exists(destDir):
            os.mkdir(destDir)
    
    userInfo = pref_utils.readUserInfo()
    if not userInfo is None:
        username = userInfo[0]
        accessKey = userInfo[1]

    if args.downloadImages is True:
        if args.wnIDs is True:
            print 'download wnIDs'
            wnids = []
            with open(args.file[0]) as f:
                for line in f:
                    if line.endswith('\n'):
                        line = line[:-1]
                        wnids.append(line)
                    else:
                        wnids.append(line)
            for id in wnids:
                print 'download wid=%s'%id
                list = downloader.getImageURLsOfWnid(id)
                downloader.downloadImagesByURLs(id, list)

    if args.downloadBoundingBox is True:
        for id in args.wnid:
            # Download annotation files
            downloader.downloadBBox(id)

    if args.downloadOriginalImages is True:
    # Download original image, but need to set key and username
        if username is None or accessKey is None:
            username = raw_input('Enter your username : ')
            accessKey = raw_input('Enter your accessKey : ')
            if username and accessKey:
                pref_utils.saveUserInfo(username, accessKey)

        if username is None or accessKey is None:
            print 'need username and accessKey to download original images'
        else:
            #for id in args.wnid:
            #    downloader.downloadOriginalImages(id, username, accessKey)
            wnids = []
            with open(args.file[0]) as f:
                for line in f:
                    if line.endswith('\n'):
                        line = line[:-1]
                        wnids.append(line)
                    else:
                        wnids.append(line)
            for id in wnids:
                print 'download wnid=%s'%id
                downloader.downloadOriginalImages(id, username, accessKey,destDir)
