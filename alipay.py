#!/usr/bin/env python
#coding:utf-8
import tornado.gen
import tornado.web
import tornado.httpserver

import alipay_config
import alipay_core


def make_payment_url(out_trade_no, subject, total_fee, service_type, body=None, show_url=None, timeout=None):
    '''
        构造支付请求参数
    '''
    order_info = {'partner': '%s' % (alipay_config.partner_id),
                  'service': '%s' % service_type,
                  '_input_charset': 'utf-8',
                  #业务参数
                  'out_trade_no': '%s' % (out_trade_no),
                  'subject': '%s' % subject,
                  'seller_id': alipay_config.partner_id,
                  'payment_type': '1',
    }

    if alipay_config.notify_url:
        order_info['notify_url'] = alipay_config.notify_url
    if alipay_config.return_url:
        order_info['return_url'] = alipay_config.return_url

    if not total_fee or total_fee <= 0.0:
        total_fee = 0.01
    order_info['total_fee'] = total_fee

    if not show_url:
        show_url = alipay_config.show_url

    order_info['show_url'] = show_url
    if body:
        order_info['body'] = body
    
    if timeout:
        order_info['it_b_pay'] = timeout

    # make request url
    url = alipay_core.make_payment_request(order_info)
    return url


class MakePaymentInfo(tornado.web.RequestHandler):
    '''
    构造一个支付请求URL
    '''

    @tornado.gen.coroutine
    def get(self, service_type, order_id):
        '''
        这里是客户端请求服务端来获取提交给支付宝的支付请求， 因为私钥放在客户端来签名的话，可能会遭遇破解，所以构造了这个服务端用来签名的方法
        '''
        self.set_status(200)
        self.set_header('Content-Type', 'application/json; charset=UTF-8')

        #构造订单信息
        STATUS_SUCCESS = 0  #成功
        STATUS_PAYED = 1  #订单已支付
        STAUTS_ORDER_NOT_EXTED = 2 #　订单不存在
        STATUS_ORDER_REFUND = 3 #订单已退款
        STATUS_ORDER_STATUS_ERROR = 4  #订单状态错误

        total_fee = 0.01  #这里将金额设为1分钱，方便测试
        body = 'test'
        if service_type == 'web':
            service_type = alipay_config.web_pay_service
        elif service_type == 'wap':
            service_type = alipay_config.wap_pay_service

        res = make_payment_url(out_trade_no=order_id, subject=order_id, total_fee=total_fee, service_type=service_type, body=body, show_url='http://www.baidu.com')
        #self.write({'status': STATUS_SUCCESS, 'res': res})
        self.write(res)


class PaymentCallback(tornado.web.RequestHandler):
    '''
    阿里支付回调
    '''

    @tornado.gen.coroutine
    def get(self):
        yield self.post()

    #这里需要做3件事情
    #1验证平台签名
    #2去阿里验证回调信息是否真实
    #3执行业务逻辑，回调订单状态
    @tornado.gen.coroutine
    def post(self):
        params = self.request.arguments
        for k, v in params.items():
            params[k] = v[0]

        check_res = alipay_core.verify_alipay_request_sign(params)  #验签
        
        if check_res == False:
            self.write('verify_alipay_request_sign fail')
            return

        #这里是去访问支付宝来验证订单是否正常
        res = yield alipay_core.verify_from_gateway(params['notify_id'])
        
        if res == False:
            self.write('verify_from_gateway fail')
            return

        if 'trade_status' not in params:
            return
        trade_status = params['trade_status']
        order_id = params['out_trade_no']  #你自己构建订单时候的订单ID
        alipay_order = params['trade_no']  #支付宝的订单号码
        total_fee = params['total_fee']  #支付总额

        '''
        下面是处理付款完成的逻辑
        '''
        print trade_status
        if trade_status == 'TRADE_SUCCESS':  #交易成功
            pass
            #TODO:这里来做订单付款后的操作
        elif trade_status == 'TRADE_FINISHED':
            pass
        elif trade_status == 'WAIT_BUYER_PAY': # trade created, wait user to pay
            pass
        elif trade_status == 'TRADE_PENDING': # 等待卖家收款（买家付款后，如果卖家账号被冻结）
            print 'WARNING: READE_PENDING'
        elif trade_status == 'TRADE_CLOSED': # 在指定时间段内未支付时关闭的交易,在交易完成全额退款成功时关闭的交易
            pass
        
        self.write('success')


def main():
    application = tornado.web.Application([
        (r'/alipay/make_payment_url/(\w*)/(\w*)', MakePaymentInfo),
        (r'/alipay/payment_callback', PaymentCallback),
    ])
    settings = {
        'debug': True,
        'autoreload': True
    }
    httpServer = tornado.httpserver.HTTPServer(application, settings)
    httpServer.listen(9998)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == '__main__':
    main()
