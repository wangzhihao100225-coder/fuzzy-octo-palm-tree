import requests

# 需要解析的高质量 CF 域名列表
domains = [
    "youxuan.cf.090227.xyz",
    "www.visa.cn",
    "mfa.gov.ua",
    "cf.tencentapp.cn"
    "cf.877774.xyz"
    "saas.sin.fan"
    "cf.cloudflare.182682.xyz"
]

# 阿里云和腾讯云的 DoH JSON API 接口
doh_servers = [
    "https://dns.alidns.com/resolve",
    "https://doh.pub/dns-query"
]

def get_ips_from_doh(domain):
    ips = set()
    headers = {"Accept": "application/dns-json"}
    success = False
    
    # 轮询 DoH 服务器，只查询 A 记录 (IPv4)
    for doh_url in doh_servers:
        params = {"name": domain, "type": "A"}
        try:
            # 设置 5 秒超时，防止工作流卡死
            response = requests.get(doh_url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    for answer in data['Answer']:
                        # 仅提取 type 1 (IPv4) 的数据
                        if answer.get('type') == 1:
                            ips.add(answer['data'])
                success = True
                break  # 当前接口查询成功，跳出内部循环，不再请求备用接口
        except Exception:
            # 发生网络错误或超时，静默失败并尝试下一个备用接口
            continue
            
    if not success:
        print(f"  [-] 警告: {domain} 的 IPv4 记录在所有 DoH 接口均解析失败")
        
    return ips

def main():
    all_ips = set()
    print("=== 开始通过国内 DoH 获取亚太优化 IP (仅限 IPv4) ===")
    
    for domain in domains:
        print(f"正在解析: {domain}...")
        domain_ips = get_ips_from_doh(domain)
        if domain_ips:
            print(f"  [+] {domain} 解析成功，提取 {len(domain_ips)} 个 IP")
            all_ips.update(domain_ips)
        
    if all_ips:
        with open("ips.txt", "w", encoding="utf-8") as f:
            for ip in sorted(all_ips):
                f.write(ip + "\n")
        print(f"\n=== 任务完成！共提取并去重 {len(all_ips)} 个 IPv4 地址 ===")
    else:
        print("\n=== 任务失败：未获取到任何 IP ===")

if __name__ == "__main__":
    main()
