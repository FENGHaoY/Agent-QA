# 微服务接口文档-支付服务 PAY-SVC

## 服务简介

支付服务（服务标识 PAY-SVC）负责发起支付、退款与对账，
部署端口 8082，基础路径 `/api/v1/pay`，代码仓库 `git@git.example.com:svc/pay.git`。

## 鉴权方式

所有接口需在请求头携带 `Authorization: Bearer <token>`，并额外校验签名 `X-Sign`。

## 主要接口

- 发起支付：`POST /api/v1/pay/payments`
- 申请退款：`POST /api/v1/pay/refunds`
- 支付查询：`GET /api/v1/pay/payments/{payId}`

## 错误码

- `PAY-40010`：支付金额非法
- `PAY-50001`：第三方支付渠道异常
- `PAY-40310`：签名校验失败

## 限流与超时

默认限流 100 QPS，单请求超时时间 5000ms，超时返回 `PAY-50400`。

## 负责人

服务负责人：孙强，邮箱 sunqiang@example.com。
