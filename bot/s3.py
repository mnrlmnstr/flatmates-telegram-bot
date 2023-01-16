import os
import boto3
import logging
from botocore.exceptions import ClientError

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_ENDPOINT = os.getenv('AWS_ENDPOINT')
AWS_REGION = os.getenv('AWS_REGION')

def get_s3_client():
    session = boto3.session.Session()
    return session.client('s3',
                          region_name=AWS_REGION,
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY)


def upload_file(file, bucket=None, object_name=None, mime_type=None, acl=None):
    """Upload a file to an S3 bucket"""
    try:
        extra_args = {}
        if acl is not None and acl == 'public-read':
            extra_args['ACL'] = acl
        if mime_type is not None:
            extra_args['ContentType'] = mime_type

        if bucket is None:
            bucket = 'default'
    
        s3_client = get_s3_client()
        s3_client.upload_file(file, bucket, object_name, ExtraArgs=extra_args)
    except ClientError as e:
        logging.error(e)
        return False
    return True

# def get_obj_url(file_name, bucket):
#     """ Get an object URL """
#     return f'https://{bucket}.{AWS_REGION}.s3.amazonaws.com/{file_name}'

def get_file_obj(file_name):
    try:
        s3_client = get_s3_client()
        response = s3_client.get_object(Bucket='flatmatebot', Key=file_name)
        return response
    except ClientError as e:
        logging.error(e)
    return None

def list_files(bucket):
    entries = []
    try:
        s3 = boto3.resource('s3',
                            region_name=AWS_REGION,
                            aws_access_key_id=AWS_ACCESS_KEY_ID,
                            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
        s3_bucket = s3.Bucket(bucket)
        for obj in s3_bucket.objects.all():
            last_modified = obj.last_modified.strftime("%Y-%m-%d %H:%M:%S")
            entry = {
                'key': obj.key,
                'size': obj.size,
                'last_modified': last_modified,
            }
            entries.append(entry)
    except ClientError as e:
        logging.error(e)
    return entries