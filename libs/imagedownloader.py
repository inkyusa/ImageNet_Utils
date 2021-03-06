import sys
import os
import time
import tarfile

if sys.version_info >= (3,):
    import urllib.request as urllib2
    import urllib.parse as urlparse
else:
    import urllib2
    import urlparse
    import urllib

class ImageNetDownloader:
    def __init__(self):
        self.host = 'http://www.image-net.org'
	self.dnStatus=0
	self.failCnt=0
	self.maxFailCnt=5 #How many times will we try to download synset in case there is an error (connection...)

    def download_file(self, url, desc=None, renamed_file=None):
        u = urllib2.urlopen(url)

        scheme, netloc, path, query, fragment = urlparse.urlsplit(url)
        filename = os.path.basename(path)
        if not filename:
            filename = 'downloaded.file'

        if not renamed_file is None:
            filename = renamed_file

        if desc:
            filename = os.path.join(desc, filename)

        with open(filename, 'wb') as f:
            meta = u.info()
            meta_func = meta.getheaders if hasattr(meta, 'getheaders') else meta.get_all
            meta_length = meta_func("Content-Length")
            file_size = None
            if meta_length:
                file_size = int(meta_length[0])
            print("Downloading: {0} Bytes: {1}".format(url, file_size))

            file_size_dl = 0
            block_sz = 8192
            while True:
                buffer = u.read(block_sz)
                if not buffer:
                    break

                file_size_dl += len(buffer)
                f.write(buffer)

                status = "{0:16}".format(file_size_dl)
                if file_size:
                    status += "   [{0:6.2f}%]".format(file_size_dl * 100 / file_size)
                status += chr(13)

        return filename

    def extractTarfile(self, filename):
        try:
            tar = tarfile.open(filename)
        except Exception, error:
            print str(error)
            print "There was an error opening tarfile. The file might be corrupt or missing."
            return 0
        tar.extractall()
        tar.close()
        return 1

    def downloadBBox(self, wnid):
        filename = str(wnid) + '.tar.gz'
        url = self.host + '/downloads/bbox/bbox/' + filename
        try:
            filename = self.download_file(url, self.mkWnidDir(wnid))
            currentDir = os.getcwd()
            os.chdir(wnid)
            self.extractTarfile(filename)
            print 'Download bbbox annotation from ' + url + ' to ' + filename
            os.chdir(currentDir)
        except Exception, error:
            print 'Fail to download' + url

    def getImageURLsOfWnid(self, wnid):
        url = 'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid=' + str(wnid)
        f = urllib.urlopen(url)
        contents = f.read().split('\n')
        imageUrls = []

        for each_line in contents:
            # Remove unnecessary char
            each_line = each_line.replace('\r', '').strip()
            if each_line:
                imageUrls.append(each_line)

        return imageUrls

    def mkWnidDir(self, destDir,wnid):
        destDirPath=os.path.join(destDir,str(wnid))
        print 'destDirPath=%s'%(destDirPath)
        if not os.path.exists(destDirPath):
            os.mkdir(destDirPath)
        return os.path.abspath(destDirPath)

    def downloadImagesByURLs(self, wnid, imageUrls):
        # save to the dir e.g: n005555_urlimages/
        wnid_urlimages_dir = os.path.join(self.mkWnidDir(wnid), str(wnid) + '_urlimages')
        if not os.path.exists(wnid_urlimages_dir):
            os.mkdir(wnid_urlimages_dir)

        for url in imageUrls:
            try:
                self.download_file(url, wnid_urlimages_dir)
            except Exception, error:
                print 'Fail to download : ' + url
                print str(error)

    def downloadOriginalImages(self, wnid, username, accesskey,destDir):
        self.dnStatus=0
        download_url = 'http://www.image-net.org/download/synset?wnid=%s&username=%s&accesskey=%s&release=latest&src=stanford' % (wnid, username, accesskey)
        while(self.dnStatus!=3 or self.dnStatus!=4):
            try:
                download_file = self.download_file(download_url, self.mkWnidDir(destDir,wnid), wnid + '_original_images.tar')
                self.dnStatus=1 #can start downloading but this doesn't mean it downloaded the wnid...
            except Exception, erro:
                print 'Fail to download : ' + download_url
                self.dnStatus=0 #can't start downloading, retry...
                self.failCnt=self.failCnt+1
                print 'failCnt=%d'%(self.failCnt)
                if self.failCnt==self.maxFailCnt:
                    self.dnStatus=4 #Skip the current wnid.
                    self.failCnt=0
                    print 'Maximum trial reached, skip wnid=%s',wnid
                    return
            if self.dnStatus==1:
                currentDir = os.getcwd()
                extracted_folder = os.path.join(self.mkWnidDir(destDir,wnid), wnid + '_original_images')
                if not os.path.exists(extracted_folder):
                    os.mkdir(extracted_folder)
                os.chdir(extracted_folder)
                if self.extractTarfile(download_file):
                    os.chdir(currentDir)
                    print 'Extract images to ' + extracted_folder
                else:
                    print 'error in tar file, skip this wnid'
                    return
                self.dnStatus=3 #finished to download the wnid.
                self.failCnt=0
                return
            else:
                print 'null download_file, try again'
