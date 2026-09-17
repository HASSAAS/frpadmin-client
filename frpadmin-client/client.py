"""Translate Supervisor options into native frpc JSON, without logging secrets."""
import json
import os
from pathlib import Path
import subprocess
import sys


def build_config(options):
    for key in ('serverAddr', 'user', 'authToken'):
        if not isinstance(options.get(key), str) or not options[key].strip():
            raise ValueError(f'{key} 必须填写')
    def port(value):
        if type(value) is not int or not 1 <= value <= 65535:
            raise ValueError('端口必须为 1–65535 的整数')
        return value
    config = {
        'serverAddr': options['serverAddr'], 'serverPort': port(options['serverPort']),
        'user': options['user'],
        'auth': {'method': 'token', 'token': options.get('serverToken', '')},
        'metadatas': {'frpadmin_token': options['authToken']},
        'transport': {'tls': {'enable': True}},
        'loginFailExit': False,
        'log': {'to': 'console', 'level': 'debug' if options.get('debug') else 'info'},
        'proxies': [],
    }
    names = set()
    for source in options.get('proxies', []):
        name = source.get('name', '')
        if not name or name in names:
            raise ValueError('代理名称不能为空或重复')
        names.add(name)
        kind = source.get('type')
        if kind not in ('tcp', 'udp', 'http', 'https'):
            raise ValueError('不支持的代理类型')
        if not source.get('localIP'):
            raise ValueError('localIP 必须填写')
        proxy = {k: source[k] for k in ('name', 'type', 'localIP')}
        proxy['localPort'] = port(source.get('localPort'))
        if kind in ('tcp', 'udp'):
            proxy['remotePort'] = port(source.get('remotePort'))
        else:
            domains = [x.strip() for x in source.get('customDomains', '').split(',') if x.strip()]
            if domains:
                proxy['customDomains'] = domains
            if source.get('subdomain'):
                proxy['subdomain'] = source['subdomain']
            if not domains and not proxy.get('subdomain'):
                raise ValueError('HTTP/HTTPS 代理需要域名或子域名')
        config['proxies'].append(proxy)
    return config


def main():
    os.umask(0o077)
    try:
        config = build_config(json.loads(Path('/data/options.json').read_text()))
    except (ValueError, KeyError, TypeError):
        print('配置无效：请检查用户名、Token、代理名称、域名和端口。', file=sys.stderr)
        return 1
    path = '/data/frpc.json'
    Path(path).write_text(json.dumps(config, ensure_ascii=False), encoding='utf-8')
    os.chmod(path, 0o600)
    check = subprocess.run(['frpc', 'verify', '-c', path], capture_output=True)
    if check.returncode:
        print('FRPC 配置校验失败，请检查加载项配置。', file=sys.stderr)
        return 1
    os.execvp('frpc', ['frpc', '-c', path])


if __name__ == '__main__':
    sys.exit(main())
