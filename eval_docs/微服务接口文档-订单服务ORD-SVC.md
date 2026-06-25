# 微服务接口文档-订单服务 ORD-SVC

## 服务简介

订单服务（服务标识 ORD-SVC）负责订单的创建、查询、取消与状态流转，
部署端口 8081，基础路径 `/api/v1/order`，代码仓库 `git@git.example.com:svc/order.git`。

## 鉴权方式

所有接口需在请求头携带 `Authorization: Bearer <token>`，令牌由统一认证中心签发。

## 主要接口

- 创建订单：`POST /api/v1/order/orders`
- 查询订单：`GET /api/v1/order/orders/{orderId}`
- 取消订单：`POST /api/v1/order/orders/{orderId}/cancel`

## 错误码

- `ORD-40001`：请求参数校验失败
- `ORD-40901`：库存不足，无法下单
- `ORD-50000`：订单服务内部错误

## 限流与超时

默认限流 200 QPS，单请求超时时间 3000ms，超时返回 `ORD-50400`。

## 负责人

服务负责人：赵敏，邮箱 zhaomin@example.com。
