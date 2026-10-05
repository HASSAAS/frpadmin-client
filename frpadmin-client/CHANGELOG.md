# 更新记录

## 2026100502

- HTTPS 独立证书模式支持 backendScheme: http，通过 https2http 连接飞牛等明文后端。
- 独立证书模式未指定后端协议时，默认使用 HTTPS。

## 2026100501

- 支持 HTTPS 代理指定证书和私钥，通过 https2https 使用独立的外网证书。
- 只读挂载 /ssl；验证证书字段配对、代理类型及绝对路径。
- 保留原有 HTTPS 直通及 HTTP 到 HTTPS 转发。
