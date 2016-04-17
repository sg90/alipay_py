#支付宝商家签约服务接口

使用Python基于Tornado框架实现。

## 支付类

## 即时到帐，手机网站支付
alipay.make_payment_url()： 构造支付请求的URL
alipay.PaymentCallback: 支付通知的RequestHandler

即时到账和手机网站支付使用service_type区分，alipay_config.web_pay_service|alipay_config.wap_pay_service

## 配置
alipay_config.py.example中配置项修改。RSA公钥、私钥、支付宝公钥、partner_id、key等。然后，重命名为alipay_config.py即可。
正式部署后，需要修改notify_url为PaymentCallback对应的URL，如果return_url不需要可以置空。

RSA公密钥：
$ openssl 进入OpenSSL程序
OpenSSL> genrsa -out rsa_private_key.pem 1024 生成私钥
OpenSSL> rsa -in rsa_private_key.pem -pubout -out rsa_public_key.pem 生成公钥
OpenSSL> exit ## 退出OpenSSL程序

