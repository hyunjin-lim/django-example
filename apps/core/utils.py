import json
import uuid
import math
import botocore.exceptions as BotoExceptions
from collections import namedtuple, OrderedDict
from base64 import b64encode, b64decode
from hashlib import sha256
from rest_framework.exceptions import PermissionDenied
from rest_framework import permissions
import boto3
from datetime import datetime
from Cryptodome.Cipher import AES
from Cryptodome.Random import new as Random
from setting.redis_connect import r
from setting.settings import (
    SECRET_KEY,
    AWS_ACCESS_KEY,
    AWS_SECRET_KEY,
    S3_BUCKET_NAME,
    CLOUD_FRONT_DISTRIBUTION_ID
)

'''
주석 처리된 함수는 서버 상의 경로에 있는 파일을 S3로 업로드하는 기능을 하는 함수
서버 상에 파일을 업로드 할 일이 있을까 하는 의문점이 들어서 작업을 멈추었다.
그런데 시드 개발을 하다가 필요성이 보여서 개발을 재개
'''


def s3_upload(origin, path):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        # 성공하면 None return
        res = s3.upload_file(origin, S3_BUCKET_NAME, path)
        return {
            'path': path,
            'url': f'{ATTACHMENT_URL}/{path}'
        }
    except Exception as e:
        return False


'''
클라이언트에서 서버로 파일을 업로드할때 서버에 저장하지 않은 메모리 오브젝트 상태로 S3에 업로드하는 함수
'''


def s3_upload_from_obj(obj, path):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        res = s3.upload_fileobj(obj, S3_BUCKET_NAME, path)
        return {
            'path': path,
            'url': '{0}/{1}'.format(ATTACHMENT_URL, path)
        }
    except Exception as e:
        return False


'''
S3 에서 파일을 삭제하는 기능을 하는 함수
만약에 완전 삭제가 아니라면 S3내 어딘가로 경로를 옮기는 함수가 필요할지도...
'''


def s3_delete(path):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=path)
    except Exception as e:
        return False

    return True


def s3_soft_delete(path):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        copy_source = {'Bucket': S3_BUCKET_NAME, 'Key': path}
        delete_file = '{0}_delete'.format(path)
        s3.copy_object(CopySource=copy_source, Bucket=S3_BUCKET_NAME, Key=delete_file)
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=path)

    except Exception as e:
        return False

    return True


def s3_restore(path):
    try:
        s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)
        restore_file = '{0}_delete'.format(path)
        copy_source = {'Bucket': S3_BUCKET_NAME, 'Key': restore_file}
        s3.copy_object(CopySource=copy_source, Bucket=S3_BUCKET_NAME, Key=path)
        s3.delete_object(Bucket=S3_BUCKET_NAME, Key=restore_file)

    except Exception as e:
        return False

    return True

def cf_invalidation(path):
    client = boto3.client('cloudfront', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)

    if path[0] != '/':
        path = '/{0}'.format(path)

    items = []
    items.append(path)

    try:
        if CLOUD_FRONT_DISTRIBUTION_ID is not None:
            distribution_id = CLOUD_FRONT_DISTRIBUTION_ID
            caller_reference = '{0}{1}'.format(
                'cli',
                datetime.now().strftime('%Y%m%d%H%M%S'),
            )
            res = client.create_invalidation(
                DistributionId=distribution_id,
                InvalidationBatch={
                    'Paths': {
                        'Quantity': len(items),
                        'Items': items,
                    },
                    'CallerReference': caller_reference
                }
            )
            return res

    except BotoExceptions.ClientError as error:
        raise error


'''
파일명 생성기 (난수화 시켜서 unique 하도록)
'''


def make_filename(filename):
    ext = filename.split('.')[-1]
    filename = "%s.%s" % (uuid.uuid4(), ext)
    return filename


def kafka_queue_reqeust(message):
    try:
        producer = KafkaProducer(
            acks=0,
            compression_type='gzip',
            bootstrap_servers=KAFKA_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )

        producer.send(KAFKA_TOPIC, value=message)
        producer.flush()

    except Exception as e:
        return False

    return True


class AESCipher:

    def __init__(self, data, key):
        self.block_size = 16
        self.data = data
        self.key = sha256(key.encode()).digest()[:32]
        self.pad = lambda s: s + (self.block_size - len(s) % self.block_size) * chr(
            self.block_size - len(s) % self.block_size)
        self.unpad = lambda s: s[:-ord(s[len(s) - 1:])]

    def encrypt(self):
        plain_text = self.pad(self.data)
        iv = Random().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return b64encode(iv + cipher.encrypt(plain_text.encode())).decode()

    def decrypt(self):
        cipher_text = b64decode(self.data.encode())
        iv = cipher_text[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_OFB, iv)
        return self.unpad(cipher.decrypt(cipher_text[self.block_size:])).decode()


def aes_encrypt(data):
    return AESCipher(AESCipher(data, SECRET_KEY).encrypt(), SUB_SECRET_KEY).encrypt()


def aes_decrypt(data):
    return AESCipher(AESCipher(data, SUB_SECRET_KEY).decrypt(), SECRET_KEY).decrypt()


def fetchone(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])

    return nt_result(*cursor.fetchone())


def fetchall(cursor):
    "Return all rows from a cursor as a namedtuple"
    desc = cursor.description
    nt_result = namedtuple('Result', [col[0] for col in desc])
    return [nt_result(*row) for row in cursor.fetchall()]


def paginate(page, per_page, total):
    page_per_block = 1
    total_page = math.ceil(total / per_page)

    prev_page = None
    if page > 1:
        prev_page = page - 1

    next_page = None

    if page < total_page:
        next_page = page + 1

    return {
        'count': total,
        'prev': prev_page,
        'next': next_page
    }


def response_with_paginate(result, paginate):
    return OrderedDict([
        ('count', paginate.get('count', 0)),
        ('prev', paginate.get('prev', None)),
        ('next', paginate.get('next', None)),
        ('result', result)
    ])


def get_token_from_header(request):
    authorization = request.META.get('HTTP_AUTHORIZATION', '')
    prefix = JWT_AUTH.get('JWT_AUTH_HEADER_PREFIX')

    if prefix in authorization:
        offset = len(prefix)
        return authorization[offset:].lstrip()

    return None


def get_user_from_token(key, token):
    key = '{0}:{1}'.format(key, token)
    if r.exists(key):
        return r.hgetall(key)

    return None


def redis_key_exists(key):
    if r.exists(key):
        return True
    return False


def set_redis_json_data(key, data):
    return r.set(key, json.dumps(data))


def get_redis_json_data(key):
    if redis_key_exists(key):
        resource = r.get(key)
        return json.loads(resource)

    return False


def permission_required(model_name, permission="api", raise_exception=False):
    mappings = {
        'GET': 'read',
        'POST': 'write',
        'FETCH': 'write',
        'PUT': 'write',
        'DELETE': 'write'
    }

    class PermissionRequired(permissions.BasePermission):
        def has_permission(self, request, view):
            permit = '{0}.{1}_{2}'.format(
                permission,
                mappings.get(request.method),
                model_name
            )
            if not request.user.has_perm(permit):
                if raise_exception:
                    raise PermissionDenied("Don't have permission")
                return False
            return True

    return PermissionRequired


def numeric(s):
    return ''.join([n for n in s if n in '0123456789'])


def is_empty(s):
    if s in [None, '', 'null']:
        return True
    return False


def str_to_bool(s):
    if s in [1, True, 'TRUE', 'True', 'true', '1']:
        return True
    return False


def set_context(request):
    is_staff = False
    if request.user is not None:
        if request.user.is_staff:
            is_staff = True
    return {
        'request': request,
        'user': request.user,
        'is_staff': is_staff
    }


def serializer_context(resource):
    context = resource.get('context', None)

    ret = {
        'context': None,
        'request': None,
        'user': None,
        'is_staff': False
    }

    if context is None:
        return ret

    user = context.get('user', None)
    if user is None or not user.is_authenticated:
        return ret

    if user.is_staff:
        ret['is_staff'] = True

    return ret


def get_or_none(classmodel, **kwargs):
    try:
        return classmodel.objects.get(**kwargs)
    except classmodel.MultipleObjectsReturned as e:
        print(e)
    except classmodel.DoesNotExist:
        return None


def obj_isset(obj, key):
    if key in dir(obj):
        return True
    return False
