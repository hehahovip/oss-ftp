# -*- coding: utf-8 -*-
import os, sys

reload(sys)
sys.setdefaultencoding('utf-8')

current_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath( os.path.join(current_path, os.pardir))
if sys.platform.startswith("linux"):
    python_lib_path = os.path.abspath( os.path.join(root_path, "python27", "unix", "lib"))
    sys.path.append(python_lib_path)
elif sys.platform == "darwin":
    python_lib_path = os.path.abspath( os.path.join(root_path, "python27", "unix", "lib"))
    sys.path.append(python_lib_path)
    extra_lib = "/System/Library/Frameworks/Python.framework/Versions/2.7/Extras/lib/python/PyObjc"
    sys.path.append(extra_lib)
elif sys.platform == "win32":
    pass
else:
    raise RuntimeError("detect platform fail:%s" % sys.platform)

import logging
from logging.handlers import RotatingFileHandler
import errno
from optparse import OptionParser

from pyftpdlib.handlers import FTPHandler
from pyftpdlib.servers import FTPServer

from oss_authorizers import OssAuthorizer 
from oss_fs import OssFS

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: 
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def set_logger(level):
    #log related
    work_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
    log_dir = work_dir + '/data/ossftp/'
    mkdir_p(log_dir)
    LOGFILE = log_dir + "ossftp.log"
    MAXLOGSIZE = 10*1024*1024 #Bytes
    BACKUPCOUNT = 30
    FORMAT = \
        "%(asctime)s %(levelname)-8s[%(filename)s:%(lineno)d(%(funcName)s)] %(message)s"
    handler = RotatingFileHandler(LOGFILE,
                mode='w',
                maxBytes=MAXLOGSIZE,
                backupCount=BACKUPCOUNT)
    formatter = logging.Formatter(FORMAT)
    handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.setLevel(level)
    logger.addHandler(handler)

def start_ftp(masquerade_address, listen_address, port, log_level, bucket_endpoints, internal):

    if log_level == "DEBUG":
        level = logging.DEBUG
    elif log_level == "INFO":
        level = logging.INFO
    elif log_level == "WARNING":
        level = logging.WARNING
    elif log_level == "ERROR":
        level = logging.ERROR
    elif log_level == "CRITICAL":
        level = logging.CRITICAL
    else:
        print "wrong loglevel parameter: %s" % log_level
        exit(1)

    authorizer = OssAuthorizer()
    if bucket_endpoints != "":
        for url in bucket_endpoints.strip().split(','):
            if len(url.split('.', 1)) != 2:
                print "url:%s format error." % (url)
                continue
            bucket_name, endpoint = url.split('.', 1)
            authorizer.bucket_endpoints[bucket_name] = endpoint
    authorizer.internal = internal
    handler = FTPHandler
    handler.permit_foreign_addresses = True
    if handler.masquerade_address != "":
        handler.masquerade_address = masquerade_address 
    handler.authorizer = authorizer
    handler.abstracted_fs = OssFS
    handler.banner = 'oss ftpd ready.'
    address = (listen_address, port)
    set_logger(level)
    server = FTPServer(address, handler)
    server.serve_forever()

def main(args, opts):
    masquerade_address = ""
    listen_address = "127.0.0.1"
    port = 2048 
    log_level = "DEBUG"
    bucket_endpoints = ""
    internal = None
    if opts.masquerade_address:
        masquerade_address = opts.masquerade_address
    if opts.listen_address:
        listen_address = opts.listen_address
    if opts.port:
        try:
            port = int(opts.port)
        except ValueError:
            print "invalid FTP port, please input a valid port like --port=2048"
            exit(1)

    if opts.loglevel:
        log_level = opts.loglevel
    
    if opts.bucket_endpoints:
        bucket_endpoints = opts.bucket_endpoints

    if opts.internal:
        internal = opts.internal
    start_ftp(masquerade_address, listen_address, port, log_level, bucket_endpoints, internal)
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("", "--masquerade_address", dest="masquerade_address", help="the ip that will reply to FTP Client, then client will send data request to this address.")
    parser.add_option("", "--listen_address", dest="listen_address", help="the address which ftpserver will listen, default is 127.0.0.1")
    parser.add_option("", "--port", dest="port", help="the local port which ftpserver will listen, default is 2048")
    parser.add_option("", "--loglevel", dest="loglevel", help="DEBUG/INFO/")
    parser.add_option("", "--bucket_endpoints", dest="bucket_endpoints", help="use this endpoint to access oss")
    parser.add_option("", "--internal", dest="internal", help="access oss from internal domain or not")
    (opts, args) = parser.parse_args()
    main(args, opts)
