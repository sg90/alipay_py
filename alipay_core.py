#coding:utf-8
__author__ = 'sg90'

import rsa
import alipay_config
import base64

SIGN_TYPE = 'SHA-1'
import urllib
import hashlib
from tornado import httpclient
import tornado.gen

def params_filter(params):
    ret = {}
    if not params:
        return ret
    for key, value in params.items():
        if key == 'sign' or key == 'sign_type' or value == '':
            continue
        ret[key] = value
    return ret


def query_to_dict(query):
    '''
    将query string转换成字典
    :param query:
    :return:
    '''
    res = {}
    k_v_pairs = query.split('&')
    for item in k_v_pairs:
        sp_item = item.split('=', 1)  #注意这里，因为sign秘钥里面可能包含'='符号，所以split一次就可以了
        key = sp_item[0]
        value = sp_item[1]
        res[key] = value

    return res


def params_to_query(params, quotes=False, reverse=False):
    query = ''
    for key in sorted(params.keys(), reverse=reverse):
        value = params[key]
        if quotes == True:
            query += str(key) + '=\'' + str(value) + '\'&'
        else:
            query += str(key) + '=' + str(value) + '&'
    query = query[0:-1]
    return query


def make_sign(message):
    '''
    签名
    '''
    private_key = rsa.PrivateKey._load_pkcs1_pem(alipay_config.RSA_PRIVATE)
    sign = rsa.sign(message, private_key, SIGN_TYPE)
    b64sing = base64.b64encode(sign)
    return b64sing

def make_md5_sign(message):
    m = hashlib.md5()
    m.update(message)
    m.update(alipay_config.key)
    return m.hexdigest()


def check_sign(message, sign):
    '''
    验证自签名
    :param message:
    :param sign:
    :return:
    '''
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(alipay_config.RSA_PUBLIC)
    return rsa.verify(message, sign, pubkey)


def check_ali_sign(message, sign):
    '''
    验证ali签名
    :param message:
    :param sign:
    :return:
    '''
    sign = base64.b64decode(sign)
    pubkey = rsa.PublicKey.load_pkcs1_openssl_pem(alipay_config.RSA_ALIPAY_PUBLIC)
    res = False
    try:
        res = rsa.verify(message, sign, pubkey)
    except Exception as e:
        print e
        res = False
    return res


def make_payment_request(params_dict):
    '''
    构造一个支付请求URL，包含最终签名
    '''
    query_str = params_to_query(params_dict) #拼接签名字符串
    sign = make_sign(query_str) #生成签名
    sign = urllib.quote_plus(sign)
    res = '%s&sign=%s&sign_type=RSA' % (query_str, sign)
    res = alipay_config.gateway + res
    return res


def verify_alipay_request_sign(params_dict):
    '''
    验证阿里支付回调接口签名
    :param params_dict: 阿里回调的参数列表
    :return:True or False
    '''
    sign = params_dict['sign']
    '''
    missingPadding = 4 - len(sign) % 4
    if missingPadding:
        sign += '=' * missingPadding
        print sign
    '''
    params = params_filter(params_dict)
    message = params_to_query(params, quotes=False, reverse=False)
    check_res = check_ali_sign(message, sign)
    return check_res


@tornado.gen.coroutine
def verify_from_gateway(notify_id):
    '''
    从阿里网关验证请求是否正确
    :param params_dict:
    :return:
    '''
    ali_gateway_url = alipay_config.gateway + 'service=' + alipay_config.notify_verify_service + '&partner=' + alipay_config.partner_id + '&notify_id=' + notify_id
    client = httpclient.AsyncHTTPClient()
    try:
        res = yield client.fetch(ali_gateway_url)
    except Exception, e:
        print 'verify_from_gateway error:' + str(e)
    
    if res.body == 'true':
        raise tornado.gen.Return(True)
    else:
        raise tornado.gen.Return(False)


if __name__ == '__main__':
    pass
