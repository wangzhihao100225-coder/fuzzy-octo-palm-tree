import requests
import json

# 需要解析的高质量 CF 域名列表
domains = [
    "Youxuan.cf.090227.xyz",
    "www.visa.cn",
    "mfa.gov.ua",
    "cf.tencentapp.cn"
]

# 阿里云和腾讯云的 DoH (DNS over HTTPS) JSON API 接口
doh_servers = [
    "https://dns.alidns.com/resolve",  # 阿里云
    "https://doh.pub/dns-query"        # 腾讯云
]

def get_ips_from_doh(domain):
    ips = set()
    headers = {
        # 告诉 DoH 服务器我们希望返回 JSON 格式的解析结果
        "Accept": "application/dns-json"
    }
    
    for doh_url in doh_servers:
        params = {
            "name": domain,
            "type": "A"  # 仅查询 IPv4 地址
        }
        try:
            print(f"正在通过 {doh_url} 解析 {domain}...")
            # 设置 5 秒超时，防止脚本卡死
            response = requests.get(doh_url, params=params, headers=headers, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                # 检查解析结果中是否包含 Answer 字段
                if 'Answer' in data:
                    for answer in data['Answer']:
                        # type 1 代表 A 记录 (IPv4)
                        if answer.get('type') == 1:
                            ips.add(answer['data'])
            else:
                print(f"  [-] 请求失败，状态码: {response.status_code}")
                
        except Exception as e:
            print(f"  [-] 请求 {doh_url} 发生异常: {e}")
            
    return ips

def main():
    all_ips = set()
    print("=== 开始通过国内 DoH 获取亚太优化 IP ===")
    
    for domain in domains:
        domain_ips = get_ips_from_doh(domain)
        if domain_ips:
            print(f"  [+] {domain} 解析成功，获得 {len(domain_ips)} 个 IP")
            all_ips.update(domain_ips)
        else:
            print(f"  [-] {domain} 未获取到 IP")
            
    # 将汇总去重后的 IP 写入 txt 文件
    if all_ips:
        with open("ips.txt", "w", encoding="utf-8") as f:
            for ip in sorted(all_ips):
                f.write(ip + "\n")
        print(f"\n=== 任务完成！共提取并去重 {len(all_ips)} 个高质量 IP ===")
    else:
        print("\n=== 任务失败：未获取到任何 IP ===")

if __name__ == "__main__":
    main()
