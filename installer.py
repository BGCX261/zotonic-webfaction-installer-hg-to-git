import xmlrpclib
import sys

def fetch_software(path, download_directory):
    try:
        cmd = "cd %s;" % (download_directory)
        cmd += "wget -c %s > /dev/null 2>&1;" % (path)
        result = server.system(session_id,  cmd)
    except:
        return None
    return 1

def extract_software(filename, download_directory):
    cmd = "cd %s;" % (download_directory)
    cmd += "tar -xvf %s > /dev/null 2>&1;" % (filename)
    return server.system(session_id,  cmd)

def configure_software(username, filename, download_directory):
    cmd = "cd %s;" % (download_directory)
    cmd += "cd %s;" % (filename)
    cmd += "./configure --prefix=/home/%s  > /dev/null 2>&1;" % (username)
    return server.system(session_id,  cmd)

def make_software(filename, download_directory):
    cmd = "cd %s;" % (download_directory)
    cmd += "cd %s;" % (filename)
    cmd += "make > /dev/null 2>&1;"

def install_erlang(user_name, download_directory):
    filename = "otp_src_R13B04.tar.gz"
    dir_name = "otp_src_R13B04"
    result = None
    #resume download of Erlang until it is finished, to beat WebFAction timeout
    while not result:
        result = fetch_software("http://www.erlang.org/download/otp_src_R13B04.tar.gz", download_directory)
    extract_software(filename, download_directory)
    configure_software(user_name, dir_name, download_directory)
    make_software(dir_name, download_directory)
    cmd = "cd %s;" % (download_directory)
    cmd += "cd otp_src_R13B04;"
    cmd += "make install > /dev/null 2>&1;"
    return server.system(session_id,  cmd)


def install_image_magick(user_name, download_directory):
    filename = "ImageMagick.tar.gz"
    dir_name = "ImageMagick-6.6.3-1"
    result = None
    while not result:
        result = fetch_software("ftp://ftp.imagemagick.org/pub/ImageMagick/ImageMagick.tar.gz", download_directory)
    extract_software(filename, download_directory)
    configure_software(user_name, dir_name, download_directory)
    make_software(dir_name, download_directory) 
    cmd = "cd %s;" % (download_directory)
    cmd += "cd ImageMagick-6.6.3-1;"
    #cmd += "make install > /dev/null 2>&1;"
    return server.system(session_id,  cmd)

def install_mercurial():
    cmd = "easy_install mercurial  > /dev/null 2>&1;"
    return server.system(session_id,  cmd)

def install_zotonic():
    cmd = "cd;"
    cmd += "hg clone https://zotonic.googlecode.com/hg/ zotonic  > /dev/null 2>&1;"
    cmd += "cd zotonic;"
    cmd += "make"
    return server.system(session_id,  cmd)

def create_downloads_directory(attempt=0):
    try:
        cmd = "mkdir tmp-erl-dir-zot-%s;" % (attempt)
        result = server.system(session_id,  cmd)
        return "tmp-erl-dir-zot-%s" % (attempt)
    except:
        if attempt > 10:
            raise
        create_downloads_directory(attempt+1)


def create(server, session_id, account, username, app_name, autostart, extra_info):
    #install mercurial in order to fetch zotonic
    install_mercurial()
    
    #create a temporary downloads directory and return its name
    download_directory = create_downloads_directory()
    
    #check for erlang and install if it is not present
    cmd = "ls ~/bin/erl"
    try:
        server.system(session_id,  cmd)
        print "Erlang is already installed"
    except:
        print install_erlang(account['username'], download_directory)
    
    #check for imagemagick and install if it is not present
    cmd = "ls ~/bin/convert"
    try:
        server.system(session_id,  cmd)
        print "ImageMagick is already installed"
    except:
        print install_image_magick(account['username'], download_directory)

    cmd = "ls ~/zotonic"
    try:
        server.system(session_id,  cmd)
        print "Zotonic is already installed"
    except:
        print install_zotonic()
    

    # Create database for Zotonic using "extra_info" as the password
    password = extra_info
    db_name = '%s_%s' % (username, app_name)
    server.create_db(session_id, db_name, 'postgresql', password)

    #create an app for zotonic
    server.create_app(session_id, app_name, 'custom_app_with_port', False, '') 

def delete(server, session_id, account, username, app_name, autostart, extra_info):
    # Delete database
    db_name = '%s_%s' % (username, app_name)
    server.delete_db(session_id, db_name, 'postgresql')
    # Delete app
    server.delete_app(session_id, app_name)

if __name__ == '__main__':
    # Parse command line arguments
    #command, username, password, machine, app_name, autostart, extra_info = sys.argv[1:]
    command, username, password, app_name, autostart, extra_info = sys.argv[1:]
    server = xmlrpclib.ServerProxy('https://api.webfaction.com/')
    session_id, account = server.login(username, password)

    # Call create or delete method
    method = locals()[command] # create or delete
    method(server, session_id, account, username, app_name, autostart, extra_info)

