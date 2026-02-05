#
# PhotoApp API functions, supporting downloading and uploading images to S3,
# along with retrieving and updating data in associated photoapp database.
#
# Initial code (initialize, get_ping, get_* helper functions):
#   Prof. Joe Hummel
#   Northwestern University
#
#   Edited by Jay Rao
#

import logging
import pymysql
import os
import boto3
import uuid

from botocore.client import Config
from configparser import ConfigParser
from tenacity import retry, stop_after_attempt, wait_exponential


#
# capture logging output in file 'log.txt'
#
logging.basicConfig(
  filename='log.txt',
  level=logging.INFO,
  format='%(asctime)s - %(levelname)s - %(message)s',
  filemode='w'
)


#
# module-level varibles:
#
PHOTOAPP_CONFIG_FILE = 'set via call to initialize()'


###################################################################
#
# get_dbConn
#
# create and return connection object, based on configuration
# information in app config file. You should call close() on 
# the object when you are done.
#
def get_dbConn():
  """
  Reads the configuration info from app config file, creates
  pymysql connection object based on this info, and returns it.
  You should call close() on the object when you are done.

  Parameters
  ----------
  N/A

  Returns
  -------
  pymysql connection object
  """

  try:
    #
    # obtain database server config info:
    #  
    configur = ConfigParser()
    configur.read(PHOTOAPP_CONFIG_FILE)

    endpoint = configur.get('rds', 'endpoint')
    portnum = int(configur.get('rds', 'port_number'))
    username = configur.get('rds', 'user_name')
    pwd = configur.get('rds', 'user_pwd')
    dbname = configur.get('rds', 'db_name')

    #
    # now create connection object and return it:
    #
    dbConn = pymysql.connect(host=endpoint,
                port=portnum,
                user=username,
                passwd=pwd,
                database=dbname,
                #
                # allow execution of a query string with multiple SQL queries:
                #
                client_flag=pymysql.constants.CLIENT.MULTI_STATEMENTS)

    return dbConn
  
  except Exception as err:
    logging.error("get_dbconn():")
    logging.error(str(err))
    raise


###################################################################
#
# get_bucket
#
# create and return bucket object, based on configuration
# information in app config file. You should call close() 
# on the object when you are done.
#
def get_bucket():
  """
  Reads the configuration info from app config file, creates
  a bucket object based on this info, and returns it. You 
  should call close() on the object when you are done.

  Parameters
  ----------
  N/A

  Returns
  -------
  S3 bucket object
  """

  try:
    #
    # configure S3 access using config file:
    #  
    configur = ConfigParser()
    configur.read(PHOTOAPP_CONFIG_FILE)
    bucketname = configur.get('s3', 'bucket_name')
    regionname = configur.get('s3', 'region_name')

    s3 = boto3.resource(
           's3',
           region_name=regionname,
           config = Config(
             retries = {
               'max_attempts': 3,
               'mode': 'standard'
             }
           )
         )

    bucket = s3.Bucket(bucketname)

    return bucket
  
  except Exception as err:
    logging.error("get_bucket():")
    logging.error(str(err))
    raise
  

###################################################################
#
# get_rekognition
#
# create and return rekognition object, based on configuration
# information in app config file. You should call close() on
# the object when you are done.
#
def get_rekognition():
  """
  Reads the configuration info from app config file, creates
  a rekognition object based on this info, and returns it.
  You should call close() on the object when you are done.

  Parameters
  ----------
  N/A

  Returns
  -------
  Rekognition object
  """

  try:
    #
    # configure S3 access using config file:
    #  
    configur = ConfigParser()
    configur.read(PHOTOAPP_CONFIG_FILE)
    regionname = configur.get('s3', 'region_name')

    rekognition = boto3.client(
                    'rekognition', 
                    region_name=regionname,
                    config = Config(
                      retries = {
                        'max_attempts': 3,
                        'mode': 'standard'
                      }
                    )
                  )

    return rekognition
  
  except Exception as err:
    logging.error("get_rekognition():")
    logging.error(str(err))
    raise


###################################################################
#
# initialize
#
# Initializes local environment need to access AWS, based on
# given configuration file and user profiles. Call this function
# only once, and call before calling any other API functions.
#
# NOTE: does not check to make sure we can actually reach and
# login to S3 and database server. Call get_ping() to check.
#
def initialize(config_file, s3_profile, mysql_user):
  """
  Initializes local environment for AWS access, returning True
  if successful and raising an exception if not. Call this 
  function only once, and call before calling any other API
  functions.
  
  Parameters
  ----------
  config_file is the name of configuration file, probably 'photoapp-config.ini'
  s3_profile to use for accessing S3, probably 's3readwrite'
  mysql_user to use for accessing database, probably 'photoapp-read-write'
  
  Returns
  -------
  True if successful, raises an exception if not
  """

  try:
    #
    # save name of config file for other API functions:
    #
    global PHOTOAPP_CONFIG_FILE
    PHOTOAPP_CONFIG_FILE = config_file

    #
    # configure boto for S3 access, make sure we can read necessary
    # configuration info:
    #
    os.environ['AWS_SHARED_CREDENTIALS_FILE'] = config_file

    boto3.setup_default_session(profile_name=s3_profile)

    configur = ConfigParser()
    configur.read(config_file)
    bucketname = configur.get('s3', 'bucket_name')
    regionname = configur.get('s3', 'region_name')

    #
    # also check to make sure we can read database server config info:
    #
    endpoint = configur.get('rds', 'endpoint')
    portnum = int(configur.get('rds', 'port_number'))
    username = configur.get('rds', 'user_name')
    pwd = configur.get('rds', 'user_pwd')
    dbname = configur.get('rds', 'db_name')

    if username == mysql_user:
      # we have password, all is good:
      pass
    else:
      raise ValueError("mysql_user does not match user_name in [rds] section of config file")
    
    #
    # success:
    #
    return True

  except Exception as err:
    logging.error("initialize():")
    logging.error(str(err))
    raise


###################################################################
#
# get_ping
#
# To "ping" a system is to see if it's up and running. This 
# function pings the bucket and the database server to make
# sure they are up and running. Returns a tuple (M, N), where
#
#   M = # of items in the photoapp bucket
#   N = # of users in the photoapp.users table
#
# If an error occurs / a service is not accessible, M or N
# will be an error message. Hopefully the error messages will
# convey what is going on (e.g. no internet connection).
#
def get_ping():
  """
  Based on the configuration file, retrieves the # of items in the S3 bucket and
  the # of users in the photoapp.users table. Both values are returned as a tuple
  (M, N), where M or N are replaced by error messages if an error occurs or a
  service is not accessible.
  
  Parameters
  ----------
  N/A
  
  Returns
  -------
  the tuple (M, N) where M is the # of items in the S3 bucket and
  N is the # of users in the photoapp.users table. If S3 is not
  accessible then M is an error message; if database server is not
  accessible then N is an error message.
  """

  def get_M():
    try:
      #
      # access S3 and obtain the # of items in the bucket:
      #
      bucket = get_bucket()

      assets = bucket.objects.all()

      M = len(list(assets))
      return M

    except Exception as err:
      logging.error("get_ping.get_M():")
      logging.error(str(err))
      raise

    finally:
      try:
        bucket.close()
      except:
        pass

  @retry(stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    reraise=True
  )
  def get_N():
    try:
      #
      # create connection to MySQL database server and then
      # execute query to retrieve # of users:
      #
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SELECT count(userid) FROM users;
            """
      
      dbCursor.execute(sql)
      row = dbCursor.fetchone()

      #
      # we get back a tuple with one result in it:
      #
      N = row[0]
      return N

    except Exception as err:
      logging.error("get_ping.get_N():")
      logging.error(str(err))
      raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  #
  # we compute M and N separately so that we can do separate exception
  # handling, and thus get partial results if one succeeds and one fails:
  #
  try:
    M = get_M()
  except Exception as err:
    M = str(err)

  try:
    N = get_N()
  except Exception as err:
    N = str(err)

  return (M, N)


###################################################################
#
# get_users
#
def get_users():
  """
  Returns a list of all the users in the database. Each element
  of the list is a tuple containing userid, username, givenname
  and familyname (in that order). The tuples are ordered by userid,
  ascending. If an error occurs, an exception is raised.
  Parameters
  ----------
  N/A
  Returns
  -------
  a list of all the users, where each element of the list is a tuple
  containing userid, username, givenname, and familyname in that order.
  The list is ordered by userid, ascending. On error an exception is
  raised
  """

  try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SELECT userid, username, givenname, familyname 
            FROM users 
            ORDER BY userid ASC
            """
      
      dbCursor.execute(sql)
      rows = dbCursor.fetchall()

      return list(rows)
  
  except Exception as err:
      logging.error("get_users():")
      logging.error(str(err))
      raise
  
  finally:
    try: 
      dbCursor.close()
    except: 
      pass
    try:
      dbConn.close()
    except:
      pass


###################################################################
#
# get_images
#
def get_images(userid = None):
  """
  Returns a list of all the images in the database. Each element
  of the list is a tuple containing assetid, userid, localname
  and bucketkey (in this order). The list is ordered by assetid,
  ascending. If a userid is given, then just the images with that
  userid are returned; validity of the userid is not checked,
  which implies that an empty list is returned if the userid is
  invalid. If an error occurs, an exception is raised.
  Parameters
  ----------
  userid (optional) filters the returned images for just this userid
  Returns
  -------
  """    
  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def get_images_inner():
    try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()

        sql = ""

        if userid:
            sql = """
              SELECT assets.assetid, users.userid, localname, bucketkey
              FROM users
              INNER JOIN assets ON users.userid = assets.userid
              WHERE users.userid = %s
              ORDER BY assets.assetid ASC
              """
            dbCursor.execute(sql, userid)
        else:
            sql = """
              SELECT assets.assetid, users.userid, localname, bucketkey
              FROM users
              INNER JOIN assets ON users.userid = assets.userid
              ORDER BY assets.assetid ASC
          """
            dbCursor.execute(sql)

        rows = dbCursor.fetchall()
        return list(rows)
    
    except Exception as err:
        logging.error("get_images():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass
  
  return get_images_inner()

###################################################################
#
# post_image
#
def post_image(userid, local_filename):
  """
  Uploads an image to S3 with a unique name, allowing the same local
  file to be uploaded multiple times if desired. A record of this
  image is inserted into the database, and upon success a unique
  assetid is returned to identify this image. The image is also
  analyzed by the Rekognition AI service to label objects within
  the image; the results of this analysis are also saved in the
  database (and can be retrieved later via get_image_labels). If
  an error occurs, an exception is raised. An invalid userid is
  considered a ValueError, "no such userid".
  Parameters
  ----------
  userid for whom we are uploading this image
  local filename of image to upload
  Page 19 of 28
  Returns
  -------
  image's assetid upon success, raises an exception on error
  """

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def post_image_inner1():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SELECT username
            FROM users 
            WHERE userid = %s
            """
      
      dbCursor.execute(sql, [userid])
      row = dbCursor.fetchone()

      if row:
        username = row[0] 
      else:
        raise ValueError("no such userid")
        
      return username    
    
    except Exception as err:
        logging.error("post_image():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def post_image_inner2():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            INSERT INTO assets (userid, localname, bucketkey)
            VALUES (%s, %s, %s);
            """
      
      dbCursor.execute(sql, [userid, local_filename, bucketkey])

      sql = """
      SELECT LAST_INSERT_ID();
      """

      dbCursor.execute(sql)
      row = dbCursor.fetchone()
      asset_id = row[0]

      dbConn.commit()

      return asset_id

    except Exception as err:
        dbConn.rollback()
        logging.error("post_image():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def post_image_inner3(asset_id, label_name, label_confidence):
      try:
        dbConn = get_dbConn()
        dbCursor = dbConn.cursor()

        sql = """
              INSERT INTO image_labels (assetid, label, confidence)
              VALUES(%s, %s, %s)
              """
        
        dbCursor.execute(sql, [asset_id, label_name, label_confidence])
        dbConn.commit()

      except Exception as err:
          dbConn.rollback()
          logging.error("post_image():")
          logging.error(str(err))
          raise
      
      finally:
        try: 
          dbCursor.close()
        except: 
          pass
        try:
          dbConn.close()
        except:
          pass

  username = post_image_inner1()

  bucket = get_bucket()

  unique_part = str(uuid.uuid4())
  bucketkey = username + "/" + unique_part + "-" + local_filename

  bucket.upload_file(local_filename, bucketkey)

  asset_id = post_image_inner2()


  rekognition = get_rekognition()
  response = rekognition.detect_labels(
            Image={
              'S3Object': {
                'Bucket': bucket.name,
                'Name': bucketkey,
              },
            },
            MaxLabels=100,
            MinConfidence=80,
          )
  labels = response['Labels']

  for label in labels:
    name = (label['Name'])
    confidence = int(label['Confidence'])
    post_image_inner3(asset_id, name, confidence)

  return asset_id

###################################################################
#
# get_image
#
def get_image(assetid, local_filename = None):
  """
  Downloads the image from S3 denoted by the provided asset. If a
  local_filename is provided, the newly-downloaded file is saved
  with this filename (overwriting any existing file with this name).
  If a local_filename is not provided, the newly-downloaded file
  is saved using the local filename that was saved in the database
  when the file was uploaded. If successful, the filename for the
  newly-downloaded file is returned; if an error occurs then an
  exception is raised. An invalid assetid is considered a
  ValueError, "no such assetid".
  Parameters
  ----------
  assetid of image to download
  local filename (optional) for newly-downloaded image
  Returns
  -------
  local filename for the newly-downloaded file, or raises an
  exception upon error
  """

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def get_image_inner():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      if local_filename:
        sql = """
              SELECT bucketkey
              FROM assets
              WHERE assetid = %s;
              """
        
        dbCursor.execute(sql, [assetid])
        row = dbCursor.fetchone()

        if row is None:
          raise ValueError("no such assetid")
        
        bucketkey = row[0]

        return [bucketkey]

      else:
        sql = """
              SELECT localname, bucketkey
              FROM assets
              WHERE assetid = %s;
              """
        
        dbCursor.execute(sql, [assetid])
        row = dbCursor.fetchone()

        if row is None:
          raise ValueError("no such assetid")
      
        cloud_filename = row[0]
        bucketkey = row[1]

        return [bucketkey, cloud_filename]

    except Exception as err:
        logging.error("get_image():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  result = get_image_inner()

  if len(result) == 2:
    local_filename = result[1]
  
  bucketkey = result[0]
    

  bucket = get_bucket()
  bucket.download_file(bucketkey, local_filename)

  return local_filename
  
  ###################################################################
#
# delete_images
#
def delete_images():
  """
  Delete all images and associated labels from the database and
  S3. Returns True if successful, raises an exception on error.
  The images are not deleted from S3 unless the database is
  successfully cleared; if an error occurs either (a) there are
  no changes or (b) the database is cleared but there may be
  one or more images remaining in S3 (which has no negative
  effect since they have unique names).
  Parameters
  ----------
  N/A
  Returns
  -------
  True if successful, raises an exception on error
  """
  
  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def delete_images_inner1():
    objects_to_delete = []
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SELECT bucketkey  
            FROM assets;
            """
      
      dbCursor.execute(sql)
      rows = dbCursor.fetchall()

      for row in rows:
        objects_to_delete.append({'Key': str(row[0])})
      
      return objects_to_delete

    except Exception as err:
        logging.error("delete_images():")
        logging.error(str(err))
        raise 
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try: 
        dbConn.close()
      except: 
        pass

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def delete_images_inner2():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SET foreign_key_checks = 0;
            """
      dbCursor.execute(sql)

      sql = """
            TRUNCATE TABLE assets;
            """
      dbCursor.execute(sql)

      sql = """
            TRUNCATE TABLE image_labels;
            """
      dbCursor.execute(sql)

      sql = """
            SET foreign_key_checks = 1;
            """
      dbCursor.execute(sql)

      sql = """
            ALTER TABLE assets AUTO_INCREMENT = 1001;
            """
      dbCursor.execute(sql)

      dbConn.commit()

    except Exception as err:
        logging.error("delete_images():")
        logging.error(str(err))
        raise 
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass
    
  objects_to_delete = delete_images_inner1()
  delete_images_inner2()

  bucket = get_bucket()

  if len(objects_to_delete) > 0:
    bucket.delete_objects(
      Delete={'Objects': objects_to_delete}
    )
  
  return True


###################################################################
#
# get_image_labels
#
def get_image_labels(assetid):
  """
  When an image is uploaded to S3, the Rekognition AI service is
  automatically called to label objects in the image. Given the
  image assetid, this function retrieves those labels. In
  particular this function returns a list of tuples. Each tuple
  is of the form (label, confidence), where label is a string
  (e.g. 'sailboat') and confidence is an integer (e.g. 90).
  The tuples are ordered by label, ascending. If an error occurs
  an exception is raised; an invalid assetid is considered a
  ValueError, "no such assetid".
  Parameters
  ----------
  image assetid to retrieve labels for
  Returns
  -------
  a list of labels identified in the image, where each element
  of the list is a tuple of the form (label, confidence) where
  label is a string and confidence is an integer. If an error
  occurs an exception is raised; an invalid assetid is considered
  a ValueError, "no such assetid".
  """

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def get_image_labels_inner():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      sql = """
            SELECT assetid 
            from assets
            WHERE assetid = %s;
            """
      
      dbCursor.execute(sql, [assetid])
      row = dbCursor.fetchone()

      if row is None:
        raise ValueError("no such assetid")

      sql = """
            SELECT label, confidence
            FROM image_labels
            WHERE assetid = %s
            ORDER BY label ASC;
            """
      
      dbCursor.execute(sql, [assetid])
      rows = dbCursor.fetchall()

      if rows is None:
        raise ValueError("no such assetid")
    
      image_labels = []

      for row in rows:
        image_labels.append((str(row[0]), int(row[1])))

      return image_labels

    except Exception as err:
        logging.error("get_image_labels():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  return get_image_labels_inner()


###################################################################
#
# get_images_with_label
#
def get_images_with_label(label):
  """
  When an image is uploaded to S3, the Rekognition AI service is
  automatically called to label objects in the image. These labels
  are then stored in the database for retrieval / search. Given a
  label (partial such as 'boat' or complete 'sailboat'), this
  function performs a case-insensitive search for all images with
  this label. The function returns a list of images, where each
  element of the list is a tuple of the form (assetid, label,
  confidence). The list is returned in order by assetid, and for
  all elements with the same assetid, ordered by label. If an
  error occurs, an exception is raised.
  Parameters
  ----------
  label to search for, this can be a partial word (e.g. 'boat')
  Returns
  -------
  a list of images that contain this label, even partial matches.
  Each element of the list is a tuple (assetid, label, confidence)
  where assetid identifies the image, label is a string, and
  confidence is an integer. The list is returned in order by
  assetid, and for all elements with the same assetid, ordered
  by label. If an error occurs, an exception is raised.
  """

  @retry(stop=stop_after_attempt(3),
  wait=wait_exponential(multiplier=1, min=2, max=30),
  reraise=True
  )
  def get_image_with_label_inner():
    try:
      dbConn = get_dbConn()
      dbCursor = dbConn.cursor()

      search_pattern = "%" + str(label) + "%"

      sql = """
            SELECT assetid, label, confidence
            FROM image_labels
            WHERE label LIKE %s
            ORDER BY assetid ASC, label ASC;
            """
      
      dbCursor.execute(sql, [search_pattern])
      rows = dbCursor.fetchall()
    
      images = []

      for row in rows:
        images.append((int(row[0]), str(row[1]), int(row[2])))

      return images

    except Exception as err:
        logging.error("get_image_with_label():")
        logging.error(str(err))
        raise
    
    finally:
      try: 
        dbCursor.close()
      except: 
        pass
      try:
        dbConn.close()
      except:
        pass

  return get_image_with_label_inner()
