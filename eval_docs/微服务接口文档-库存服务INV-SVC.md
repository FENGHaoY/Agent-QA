# 微服务接口文档-库存服务 INV-SVC

## 服务简介

库存服务（服务标识 INV-SVC）负责库存的查询、扣减与回补，
部署端口 8083，基础路径 `/api/v1/inventory`，代码仓库 `git@git.example.com:svc/inventory.git`。

## 鉴权方式

所有接口需在请求头携带 `Authorization: Bearer <token>`，内部调用走 mTLS。

## 主要接口

- 扣减库存：`POST /api/v1/inventory/deductions`
- 回补库存：`POST /api/v1/inventory/restorations`
- 查询库存：`GET /api/v1/inventory/stocks/{sku}`

## 错误码

- `INV-40020`：SKU 不存在
- `INV-60001`：库存不足，扣减失败
- `INV-50000`：库存服务内部错误

## 限流与超时

默认限流 300 QPS，单请求超时时间 2000ms，超时返回 `INV-50400`。

## 负责人

服务负责人：周婷，邮箱 zhouting@example.com。
