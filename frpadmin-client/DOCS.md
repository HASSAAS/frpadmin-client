# FRPAdmin 专属客户端

独立重写的 Home Assistant 本地加载项，参考冬瓜 FRP Client 的 YAML 使用方式。
支持 amd64 / aarch64，内置 FRP 0.71.0；无需 NET_ADMIN、TUN 或 Supervisor API 权限。

## 安装

1. 将整个 `frpadmin-client` 目录复制到 Home Assistant 的 `/addons/frpadmin-client`。
   使用 Samba 时是 `addons` 共享，不能放到 `config` 共享。
2. 在加载项商店检查更新/刷新，找到本地加载项 **FRPAdmin Client**，点击安装。
3. 首次构建需要访问 Docker Hub、Alpine 软件源和 GitHub Releases。
4. 填写下面的 YAML，保存并启动；查看日志确认 login success 和 start proxy success。
5. 停止原客户端中同名、同域名的代理，避免注册冲突。

## 配置示例

```yaml
serverAddr: fnos.f.17paixie.com
serverPort: 7000
user: scliao
authToken: "填写 FRPAdmin 为 scliao 分配的个人 Token"
serverToken: "填写 FRPS 的 auth.token，与面板共享 token 保持一致"
debug: false
proxies:
  - name: HomeAssistant9_http
    type: http
    localIP: 192.168.123.9
    localPort: 80
    customDomains: ha9.f.17paixie.com
  # 内网目标只接受 HTTPS 时（如 https://192.168.123.9:80），加一行 backendScheme：
  - name: HomeAssistant9_http_tls
    type: http
    localIP: 192.168.123.9
    localPort: 80
    backendScheme: https
    customDomains: ha99.f.17paixie.com
```

`authToken` 是个人凭据，通过 TLS 连接中的 `metadatas.frpadmin_token` 传递。
`serverToken` 是 FRPS 原生连接凭据，写入 `auth.token`。两者用途不同，不能互换。
若服务端明确配置空连接 Token，此处也填写空字符串；不要为了连接成功擅自清空服务端凭据。
`backendScheme: https` 用于后端只提供 HTTPS 的场景：frps 的 http 类型会把明文请求转发给 frpc，
frpc 再用 `https2http` 插件以 HTTPS 请求本地目标，此时不再下发 localIP/localPort。
不加该字段时按明文 HTTP 转发；若后端只接受 HTTPS，会表现为 frps 返回 404 且出向流量为 0。
`type: https` 是 TLS 直通（SNI 路由），不需要也不接受该插件。
域名支持逗号分隔；HTTP/HTTPS 不填写 remotePort，TCP/UDP 必须填写。
用户名、个人 Token 与面板一致；面板登记代理名填 `HomeAssistant9_http`，不要手动加用户名。
FRPC 实际注册名称自动变成 `scliao.HomeAssistant9_http`。
配置文件写入 `/data/frpc.json`，权限 0600；启动前调用 frpc verify，退出信号直接传给 frpc。

## 必须同步更新 FRPAdmin 服务端

旧版接口不能识别官方插件请求，不能只安装客户端。
本次配套修改 main.py、store.py、configgen.py、static/app.js、Dockerfile 后，在飞牛执行：

```sh
cd /vol1/1000/Docker/frp-admin
docker compose up -d --build
```

面板中设置鉴权模式为 plugin，严格模式开启；共享 token 填现有 FRPS 的 auth.token，
钩子密钥留空（原生 FRPS 插件没有此自定义请求头配置）。
创建/核对 scliao 用户、到期时间，以及对应 HTTP 代理的名称、归属、域名、启用状态。
本地 IP/端口不随 NewProxy 请求发送，服务端无法从该请求校验本地目标。
配额仍由面板登记规则时管理；到期/禁用在登录和新建代理时检查，不会主动踢掉已建立的连接。

在现有 frps.toml 的末尾追加以下插件段（已有同名段则修改，不要重复追加）：

```toml
[[httpPlugins]]
name = "frp-admin"
addr = "192.168.123.3:8080"
path = "/api/frps/auth"
ops = ["Login", "NewProxy"]
```

保留原有 auth 和 webServer 配置，确保它们在插件段之前。
先备份 FRPS 配置，再重启 frps 容器使配置生效；插件启用后旧客户端也必须携带用户元数据。
本次交付没有修改运行中 FRPS 的配置或自动重启服务。

## 验证和排错

- `invalid user token`：检查 authToken、user，以及是否已更新管理服务。
- FRPS token 校验失败：检查 serverToken 与 FRPS auth.token。
- `proxy not registered...`：检查面板代理名称、归属和启用状态。
- `domain mismatch`：域名必须与面板登记一致。
- 访问 `http://ha9.f.17paixie.com:2080`，需 DNS 与入口端口转发正确。
- Home Assistant 返回 400 时，按实际代理来源配置 trusted_proxies，不要使用全网信任。

## 参考

- https://github.com/waxgourd-ha/waxgourd-addons/tree/main/frp-client
- https://gofrp.org/en/docs/features/common/server-plugin/
- https://developers.home-assistant.io/docs/apps/configuration/

本加载项脚本为独立实现，未复制原项目脚本；FRP 二进制遵循随镜像附带的 Apache-2.0 许可证。
