#支付宝商家签约服务接口

使用Python基于Tornado框架实现。

## 支付类

## 即时到帐，手机网站支付
alipay.make_payment_url()： 构造支付请求的URL
alipay.PaymentCallback: 支付通知的RequestHandler

## 备注
正式部署后，需要修改notify_url为PaymentCallback对应的URL，注释掉return_url

