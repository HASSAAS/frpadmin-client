# FRPAdmin Home Assistant Add-ons

FRPAdmin 专属 Home Assistant 客户端仓库。

## 从 GitHub 安装

1. 在 Home Assistant 中打开「设置 → 加载项 → 加载项商店」。
2. 从右上角菜单打开「仓库」，添加 `https://github.com/HASSAAS/frpadmin-client`。
3. 刷新商店，找到 **FRPAdmin Client** 并安装。
4. 按 [客户端说明](frpadmin-client/DOCS.md) 填写配置，并同步更新 FRPAdmin 服务端。

客户端支持 amd64 / aarch64，在 Home Assistant 本地构建镜像。
本仓库只包含客户端，不包含 FRPAdmin 数据库和服务端凭据。

## 认证字段

- `user`：FRPAdmin 用户名。
- `authToken`：FRPAdmin 为该用户分配的个人 Token。
- `serverToken`：FRPS 原生连接 Token，必须与服务端 `auth.token` 一致。

个人 Token 通过 `metadatas.frpadmin_token` 传递，需要配套的 FRPAdmin 插件接口支持。
