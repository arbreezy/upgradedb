#!/usr/bin/env python
import os
import re
import sys
import socket
import collections
import glob
import pymysql
import logging
import logging.handlers
import datetime


def takedigits(filenames):
    # we will keep a dictionary with filenames and the number, so we can easily keep a correlation
    # between sql files and version numbers.
    resources = {}
    for filename in filenames:
        # this regex may covers more use cases than the original use case.
       number = re.findall(r'\b\d+\b',filename)
       if len(number) != 1:
           print "[ERROR] There is either a typo or more numbers than needed. Exiting.. "
           raise SystemExit
       else:
           resources.update({int(number[0]):filename})
    sqldict = collections.OrderedDict(sorted(resources.items()))

    return sqldict


def main():
    # tests for argument orders.
    #one more for the name of the script.
    if len(sys.argv) != 6:
        print "[ERROR] We expect 5 cli arguments.\ne.g $ sqlupgrade.py directory-with-sql-scripts username-for-the-db db-host db-name db-password. \n"
    else:
        # parse filename on the given dir path. I was thinking to check if it isn't an absolute path
        # add the pwd + relativ path - but its much safer to go only with absolute paths.
        if os.path.isdir(sys.argv[1]) and os.path.isabs(sys.argv[1]):
                if sys.argv[2].isalpha():
                    try:
                        dbhost = socket.gethostbyname(sys.argv[3])
                    except socket.gaierror, err:
                        print "cannot resolve hostname", err
                        raise SystemExit
                    # check if db name is alphnum with no spaces.
                    if sys.argv[4].isalnum():
                        #regex to check password arg - expecting at least 8 digits.
                        if  re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', sys.argv[5]):
                            # we have all the arguments to start our upgrade.
                            # avoid to double check if there is a final slash in the dir path :)
                            os.chdir(sys.argv[1])
                            filenames = glob.glob("*.sql")
                            resources = takedigits(filenames)
                            # compare with DB current version 
                            higher_number = resources.keys()[-1]
                            #Open connection with mysql
                            connection = pymysql.connect(host=sys.argv[3], port=3306, user=sys.argv[2], passwd=sys.argv[5], db=sys.argv[4])
                            current_version = None
                            try:
                                cur = connection.cursor()
                                cur.execute("SELECT * FROM versionTable")
                                for row in cur:
                                    current_version = row
                                current_version = current_version[0]
                            finally:
                                connection.close()
                            if current_version is None:
                                print "[ERROR] Couldn't extract the current version of DB. Exiting..\n"
                                raise SystemExit
                            elif current_version == higher_number:
                                print "[INFO] No need to run migration checks. Exiting..\n"
                                raise SystemExit

                            elif current_version < higher_number:
                                # DB version changed, lets find and execute the appropriate sql files
                                # I will make an assumption that each sql file containes one query only.
                                # If that's not the use case I would split the queries in a file with the ';' delimeter
                                # *.read().split(';')) and then apply them
                                logging.basicConfig(filename='example.log',level=logging.DEBUG)
                                today = datetime.date.today()
                                formatted_date = today.strftime('Applied in %d, %b %Y')
                                for key,sqlscript in resources.items():
                                    #our Dict is sorted so we can just loop in the items - last element is the higher one
                                    if key > current_version:
                                        #execute the sql script
                                        sqlfile = open(sqlscript, 'r')
                                        sql =  " ".join(sqlfile.readlines()).replace(';','')
                                        # TODO: make connection a small function to return the object
                                        connection = pymysql.connect(host=sys.argv[3], port=3306, user=sys.argv[2], passwd=sys.argv[5], db=sys.argv[4])
                                        try:
                                            cur = connection.cursor()
                                            print "[INFO] Running sql query from file: %s" %sqlscript
                                            cur.execute(sql)
                                            logging.debug(formatted_date + '\n' + sqlscript)
                                            # commit the changes
                                            connection.commit()
                                        except pymysql.InternalError as error:
                                            code, message = error.args
                                            print message
                                            raise SystemExit
                                        finally:
                                            connection.close()
                                
                                    else:
                                        continue
                            # update our DB version - one last mysql connection
                            current_version = higher_number
                            connection = pymysql.connect(host=sys.argv[3], port=3306, user=sys.argv[2], passwd=sys.argv[5], db=sys.argv[4])
                            try:
                                cur = connection.cursor()
                                update = "UPDATE versionTable SET version = %s"
                                cur.execute(update,(current_version))
                                connection.commit()
                            except pymysql.InternalError as error:
                                code, message = error.args
                                print message 
                                raise SystemExit
                            finally:
                                connection.close()

                        else:
                            print "[ERROR] Password should be at least 8 characters."
                            raise SystemExit
                    else:
                        print "[ERROR] Wrong DB name."
                        raise SystemExit
                else:
                    print "[ERROR] Username is wrong.\n Please try again.."
                    raise SystemExit
        else:
            print "[ERROR] We expect an absolute directory path. Exiting..\n"

if __name__ == "__main__":
    main()
