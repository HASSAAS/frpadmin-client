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

## 完整配置示例：内网 HTTPS + 外网独立证书

在加载项的「配置」页面切换为 YAML 编辑，填写下面内容并保存。
以下域名、IP、用户名和文件名仅为示例；两个 Token 必须填写你自己的值。

```yaml
serverAddr: frps.example.com
serverPort: 7000
user: your_user
authToken: "你的 FRPAdmin 个人 Token"
serverToken: "你的 FRPS 连接 Token"
debug: false
proxies:
  - name: homeassistant_https
    type: https
    localIP: 192.168.1.10
    localPort: 443
    customDomains: ha.example.com
    sslCertificate: /ssl/fullchain.pem
    sslKey: /ssl/privkey.pem
```

该配置的访问路径是：浏览器 → FRPS 的 HTTPS 入口 → HA 客户端的
`https2https` 插件（使用外网证书）→ 内网 Home Assistant HTTPS。
内网 Home Assistant 可以继续使用自己的局域网证书。

### 连接和认证字段

| 字段 | 填什么 | 说明 |
| --- | --- | --- |
| `serverAddr` | FRPS 域名或 IP | 不带 `http://`、端口和路径；不是 FRPAdmin 管理网页地址 |
| `serverPort` | FRPS 的 `bindPort` | 常见为 7000，须以服务端实际配置为准；不是网页或外网访问端口 |
| `user` | FRPAdmin 用户名 | 必须与面板中规则归属的用户一致 |
| `authToken` | 该用户的个人 Token | 用于 FRPAdmin 用户鉴权，不能用 SSH 密码代替 |
| `serverToken` | FRPS 的 `auth.token` | 与个人 Token 是两项不同凭据；仅当服务端配置为空时才留空 |
| `debug` | `false` 或 `true` | 日常用 `false`；排查问题可临时改为 `true` |
| `proxies` | 代理规则列表 | 每条规则以 `- name:` 开始，可以配置多条 |

### 每条代理规则的字段

| 字段 | 填什么 | 说明 |
| --- | --- | --- |
| `name` | 面板登记的代理名称 | 同一客户端内不可重复；填写原始名称，不要手动加 `用户名.` 前缀 |
| `type` | `http`、`https`、`tcp` 或 `udp` | 决定 FRPS 如何转发请求 |
| `localIP` | 内网目标 IP 或主机名 | 目标必须能从 HA 加载项访问 |
| `localPort` | 内网服务监听端口 | 如 HA 已配置 HTTPS 443，就填 443；不是外网入口端口 |
| `customDomains` | 外网域名 | HTTP/HTTPS 使用；多个域名用英文逗号分隔，不带协议、端口和路径 |
| `subdomain` | 子域名名称 | 可替代自定义域名，但须服务端已配置 `subdomainHost` |
| `backendScheme` | `http` 或 `https` | HTTP 规则连接 HTTPS 后端时设为 `https`；HTTPS 独立证书模式也支持此字段：设为 `http` 时使用 https2http；省略则连接 HTTPS 后端 |
| `sslCertificate` | `/ssl/fullchain.pem` 等绝对路径 | 仅 HTTPS 类型支持；与 `sslKey` 同时填写才启用独立外网证书 |
| `sslKey` | `/ssl/privkey.pem` 等绝对路径 | 与证书匹配的私钥；不能填写 Windows 文件路径 |
| `remotePort` | FRPS 上的 TCP/UDP 入口端口 | TCP/UDP 必填；HTTP/HTTPS 不填 |

### 证书文件放哪里

1. 将外网域名的 PEM 证书链和对应私钥放入 Home Assistant 的 **ssl 共享**。
2. 若共享中文件名为 `fullchain.pem` 和 `privkey.pem`，配置路径就是
   `/ssl/fullchain.pem` 和 `/ssl/privkey.pem`。加载项只读挂载该目录。
3. 证书须在有效期内并匹配 `customDomains`，私钥须与证书匹配。
4. 证书更新后重启客户端，使其重新加载文件。不要把私钥或 Token 上传到 GitHub。

## 其他常见用法

以下示例只展示 `proxies`，连接和认证字段仍需保留。

### HTTP 入口连接 HTTPS 后端

适用于外网走 HTTP、内网 Home Assistant 只提供 HTTPS 的情况。

```yaml
proxies:
  - name: homeassistant_http
    type: http
    localIP: 192.168.1.10
    localPort: 443
    backendScheme: https
    customDomains: ha.example.com
```

客户端使用 `http2https` 插件连接内网。浏览器这一段仍是 HTTP；登录 HA 建议使用 HTTPS 入口。
若内网服务是普通 HTTP，则将 `localPort` 改为实际 HTTP 端口，并将
`backendScheme` 设为 `http` 或省略该字段。

### HTTPS 直通

适用于内网服务本身已使用与外网域名匹配的证书。

```yaml
proxies:
  - name: homeassistant_passthrough
    type: https
    localIP: 192.168.1.10
    localPort: 443
    customDomains: ha.example.com
```

不填写 `sslCertificate` 和 `sslKey` 时保持 TLS 直通。
浏览器看到的是内网服务的证书；若内网只配置 IP 自签证书，访问外网域名仍可能提示证书错误。

### TCP 转发

```yaml
proxies:
  - name: tcp_service
    type: tcp
    localIP: 192.168.1.20
    localPort: 12345
    remotePort: 23456
```

通过 FRPS 主机的 23456 端口访问内网 12345 端口。
服务端必须允许该端口，防火墙和路由转发也须放行。UDP 配置方式相同，将 `type` 改为 `udp`。

## 面板规则、DNS 和访问端口

- 在 FRPAdmin 中登记同名规则，归属用户、类型、域名和启用状态必须与客户端一致。
- 外网域名的 DNS 应指向能访问 FRPS 入口的地址，且入口端口须放行或正确转发。
- HTTP 入口取决于 FRPS 的 `vhostHTTPPort`，HTTPS 入口取决于 `vhostHTTPSPort`。
- 例如 HTTP 入口为 2080、HTTPS 入口为 2443，则分别访问
  `http://ha.example.com:2080/` 和 `https://ha.example.com:2443/`。
  若公网路由另做端口映射，以公网入口端口为准。
- FRPAdmin 管理页面端口、FRPS 连接端口、内网目标端口和外网入口端口是不同用途，不能混填。
- 同一个代理名或域名不要同时在 NAS 客户端和 HA 客户端注册；迁移时先停止旧规则。

## 保存后怎么检查

1. 保存配置并启动/重启加载项。
2. 日志应出现 `login to server success`，并且每条规则出现 `start proxy success`。
3. 打开对应外网地址，确认页面能加载；HTTPS 还需核对证书域名和有效期。
4. 若 HA 返回 400，按实际代理来源配置 `use_x_forwarded_for` 和 `trusted_proxies`，
   详细说明见 [Home Assistant 官方 HTTP 文档](https://www.home-assistant.io/integrations/http/)。

| 现象 | 检查方向 |
| --- | --- |
| 无法连接服务端 | `serverAddr`、`serverPort`、DNS 和 FRPS 端口连通性 |
| `invalid user token` | 用户名、个人 Token、用户有效期和 FRPAdmin 插件接口 |
| FRPS Token 校验失败 | `serverToken` 是否与服务端 `auth.token` 一致 |
| `proxy not registered` / `domain mismatch` | 面板中代理名称、归属、类型、域名和启用状态 |
| 代理重复或域名被占用 | 是否仍有旧客户端运行同名/同域名规则 |
| HTTP 访问 HTTPS 后端失败 | 是否填写 `backendScheme: https` 和正确的内网端口 |
| HTTPS 提示证书不匹配 | 是直通还是独立证书模式；证书是否覆盖外网域名 |
| 证书配置无法启动 | 两个证书字段是否同时填写，文件是否存在、路径是否正确 |

更多服务端插件配置和安装细节见 [客户端完整说明](frpadmin-client/DOCS.md)。
