
# VXLAN & EVPN 技术总结清单（中文白皮书完整版）
**Author: Helen Liu**  
*(Computer Science & Network Systems)*

---

## 一、VXLAN 封装结构与原理（RFC 7348）

VXLAN 是一种运行在三层网络上的二层 Overlay 技术。
通过在原始以太帧外层封装 UDP + VXLAN Header，将广播域扩展到 IP 网络中。

```bash
Outer Ethernet Header
→ Outer IP Header
→ Outer UDP Header (Dst Port = 4789)
→ VXLAN Header (8 bytes)
→ Inner Ethernet Frame
```
| 层级 | 说明 |
|------|------|
| Outer Ethernet Header | 用于底层物理转发。 |
| Outer IP Header | 源IP=VTEP1，目的IP=VTEP2。 |
| Outer UDP Header | 源端口随机，目的端口4789。 |
| VXLAN Header | Flags=0x08 表示 VNI 有效。 |
| Inner Ethernet Frame | 原始以太帧。 |

---

## 二、L2VNI / L3VNI 概念与互通机制

| 层级 | 标识 | 控制平面 | 一致性要求 | 互通机制 |
|------|------|-----------|-------------|-----------|
| 二层域 | L2VNI | EVPN Type-2 | 必须相同 | 不同 L2VNI 通过三层互通。 |
| 三层域 | L3VNI + RT | EVPN Type-5 | 可不同，RT 相同即可互通 | RT 控制 VRF 路由导入导出。 |

---

## 三、VXLAN 三层互通（L3VNI）

当不同 L2VNI 的主机需要互通时，需通过 L3VNI 进行跨网段转发。

```bash
HostA (L2VNI 5001) → L3VNI 6001 → HostB (L2VNI 5002)
```

---

## 四、VXLAN 与 MPLS L3VPN 对比

| 特性 | MPLS L3VPN | VXLAN EVPN |
|------|-------------|-------------|
| 封装协议 | MPLS | UDP/VXLAN |
| 控制平面 | MP-BGP VPNv4 | MP-BGP EVPN |
| 二层隔离 | VLAN/VRF | L2VNI |
| 三层隔离 | VRF | L3VNI |
| 封装端点 | PE | VTEP |
| 路由传播 | RD/RT | RD/RT |
| 典型场景 | 多租户WAN | 数据中心Overlay |

---

## 五、核心逻辑总结

1. L2VNI 无法由 RT 控制  
2. 不同 L2VNI 必须经 L3VNI 路由互通  
3. L3VNI 的互通取决于 RT

---

## 六、🧱 EVPN 五类 Route Type 深度说明 + 场景应用表  
（基于 RFC 7432 / RFC 8365）

| 场景 | 关键 Route Type | 详细说明 |
|------|----------------|-----------|
| **EVPN MAC 学习 / ARP 抑制** | **Type 2 – MAC/IP Advertisement Route** | 🔹 **作用**：在 BGP EVPN 控制平面中分发 MAC 和 IP 绑定。替代传统二层泛洪学习。<br>🔹 **触发**：当 PE/VTEP 学习到新的 MAC （或 MAC+IP 绑定）时，会发布 Type 2 NLRI。<br>🔹 **关键字段**：<br> • Ethernet Tag ID (VNI/VLAN)<br> • MAC Address (6 B)<br> • IP Address (可选，用于 ARP 抑制)<br> • MPLS Label / VNI<br> • Sequence Number (防止 MAC 迁移乱序)<br>🔹 **控制平面结果**：其他 VTEP 接收此 NLRI 后建立 MAC/IP → VTEP 映射表。<br>🔹 **数据平面效果**：<br> • 远端 VTEP 不再泛洪 ARP 请求（ARP suppress）；<br> • 可以直接单播封装至目标 VTEP。<br>🔹 **抓包特征**：<br> • BGP UPDATE 中 NLRI Type=2；<br> • MP_REACH_NLRI 段包含 MAC/IP；<br> • 常伴随 “MAC Mobility Extended Community”。 |
| **VTEP 加入广播域** | **Type 3 – Inclusive Multicast Ethernet Tag (IMET)** | 🔹 **作用**：让所有 VTEP 知道谁属于这个 VNI（EVI），以建立 BUM 复制树。<br>🔹 **触发**：新 VTEP 加入某 L2VNI 时发送。<br>🔹 **关键字段**：<br> • Ethernet Tag ID（EVI/VNI）<br> • Originating Router’s IP（VTEP Loopback IP）<br> • Label/VNI 指示 Replication ID<br>🔹 **控制平面结果**：所有 VTEP 建立 IMET List，用于 BUM 转发。<br>🔹 **数据平面效果**：广播/未知/多播流量复制至 IMET 成员。<br>🔹 **抓包特征**：<br> • BGP UPDATE NLRI Type=3；<br> • Router’s IP = VTEP Loopback；<br> • Flags 通常含 IMET 社区属性。 |
| **Dual-Homing Active/Active** | **Type 1 + Type 4** | 🔹 **Type 1 (EAD Route)**：通知同一 Ethernet Segment (ES) 的存在。<br> • 字段：ESI(10 B)、Ethernet Tag ID、Label。<br> • 作用：让远端 PE 知道哪些 PE 共享同一 CE 连接。<br>🔹 **Type 4 (ES Route)**：用于 DF 选举（防环路）。<br> • 字段：ESI、Originating Router IP。<br> • 作用：在多个 PE 间选出 DF (Designated Forwarder)。<br>🔹 **触发**：当 CE 接入两个 PE（ESI 相同）时，两个 PE 都会发布 Type 1 & Type 4。<br>🔹 **控制平面结果**：远端 PE 可识别 ESI 拓扑，并由 DF 负责单一方向转发 BUM 流量。<br>🔹 **数据平面效果**：避免 Active/Active 双发导致的广播环路。<br>🔹 **抓包特征**：<br> • BGP UPDATE NLRI Type=1/4；<br> • 属性中 ES-Import RT 相同。 |
| **L3VNI 互通（跨子网路由）** | **Type 5 – IP Prefix Route** | 🔹 **作用**：在 EVPN VRF 中通告 L3 前缀，实现跨 L2VNI 路由。<br>🔹 **触发**：当 VRF 学习到新前缀（例如 192.168.20.0/24）时，PE 发布 Type 5 NLRI。<br>🔹 **关键字段**：<br> • IP Prefix + Length<br> • RD（区分租户）<br> • RT（导入导出控制）<br> • Label/VNI（L3VNI 标识）<br>🔹 **控制平面结果**：其他 VTEP 在其 VRF 中安装对应前缀。<br>🔹 **数据平面效果**：L2VNI A ↔ L3VNI ↔ L2VNI B 实现跨子网互通。<br>🔹 **抓包特征**：<br> • BGP UPDATE NLRI Type=5；<br> • Prefix 字段明确（IPv4/IPv6）。 |
| **抓包识别** | **NLRI Type 字段 (1–5)** | 🔹 **定位方法**：在 BGP UPDATE 的 MP_REACH_NLRI 中查看 EVPN NLRI Type 字节：<br> • 0x01 → EAD Route (Type 1)<br> • 0x02 → MAC/IP Advertisement (Type 2)<br> • 0x03 → IMET Route (Type 3)<br> • 0x04 → ES Route (Type 4)<br> • 0x05 → IP Prefix Route (Type 5)<br>🔹 **常见属性组合**：<br> • Type 2 + Route-Target → MAC/IP 学习<br> • Type 3 + IMET RT → 广播树<br> • Type 5 + VRF RT → L3VNI 路由传播 |

---

## 七、测试与抓包验证要点（增强版）

### ① VXLAN Header 封装验证
```bash
udp.port == 4789
```
**Wireshark 示例结构**
```bash
Outer Ethernet Header
Outer IP Header
Outer UDP Header (Dst Port = 4789)
VXLAN Header: Flags=0x08, VNI=5001
Inner Ethernet Frame: Src=00:11:22:33:44:55, Dst=aa:bb:cc:dd:ee:ff
```

### ② EVPN Type 2 – MAC/IP Advertisement 验证
```bash
bgp.nlri.type == 2
```
**Wireshark 片段**
```bash
BGP UPDATE Message
 ├─ MP_REACH_NLRI
 │   ├─ NLRI Type: 2 (MAC/IP Advertisement)
 │   ├─ Ethernet Tag ID: 5001
 │   ├─ MAC: 00:11:22:33:44:55
 │   ├─ IP: 10.1.1.10
 │   ├─ Label/VNI: 5001
 │   └─ MAC Mobility Seq#: 0
```
**CLI 验证**
```bash
VTEP1# show bgp l2vpn evpn route type 2
Route Distinguisher: 10.1.1.1:5001
  EVPN MAC/IP Advertisement
  MAC: 00:11:22:33:44:55  IP: 10.1.1.10
  ETag: 5001  VNI: 5001  Next-hop: 10.1.1.2
  Ext-Community: RT:100:5001, MAC Mobility Seq#: 0
```

### ③ EVPN Type 3 – IMET Route 验证
```bash
bgp.nlri.type == 3
```
**Wireshark 显示**
```bash
BGP UPDATE
 ├─ MP_REACH_NLRI
 │   ├─ NLRI Type: 3 (IMET Route)
 │   ├─ ETag: 5001
 │   ├─ Originating Router IP: 10.1.1.1
 │   └─ VNI: 5001
```
**CLI 验证**
```bash
VTEP2# show bgp l2vpn evpn imet
EVI: 5001
  Originating Router: 10.1.1.1
  Originating Router: 10.1.1.2
  Originating Router: 10.1.1.3
```

### ④ EVPN Type 5 – IP Prefix Route 验证
```bash
bgp.nlri.type == 5
```
**Wireshark 示例**
```bash
BGP UPDATE
 ├─ MP_REACH_NLRI
 │   ├─ NLRI Type: 5 (IP Prefix Route)
 │   ├─ IP Prefix: 10.1.2.0/24
 │   ├─ RD: 10.1.1.1:6001
 │   ├─ RT: 100:6001
 │   ├─ Label/VNI: 6001
 │   └─ Next-hop: 10.1.1.2
```
**CLI 验证**
```bash
VTEP1# show bgp l2vpn evpn route type 5
Route Distinguisher: 10.1.1.1:6001
  Network: 10.1.2.0/24
  Label/VNI: 6001
  Next-hop: 10.1.1.2
  Ext-Community: RT:100:6001
```

### ⑤ ESI & DF 选举验证（Type 1 + Type 4）
```bash
bgp.nlri.type == 1 || bgp.nlri.type == 4
```
**Wireshark 示例**
```bash
BGP UPDATE
 ├─ NLRI Type: 1 (EAD Route)
 │   ├─ ESI: 0000:0000:0001
 │   ├─ Ethernet Tag: 5001
 │   └─ Label: 5001
 ├─ NLRI Type: 4 (ES Route)
 │   ├─ ESI: 0000:0000:0001
 │   ├─ Originating Router IP: 10.1.1.1
 │   └─ DF Election Info: Alg=Default
```
**CLI 验证**
```bash
PE1# show evpn ethernet-segment
ESI: 0000:0000:0001
  DF Role: Designated Forwarder
  DF Algorithm: Default
  Peers: 10.1.1.2
PE2# show evpn ethernet-segment
ESI: 0000:0000:0001
  DF Role: Non-DF
```

---

## 八、RFC 对照表

| 类别 | RFC | 内容 |
|------|------|------|
| VXLAN 数据面 | RFC 7348 | VXLAN 封装格式 |
| EVPN 控制平面 | RFC 7432 | BGP EVPN 核心机制 |
| EVPN over VXLAN | RFC 8365 | 数据中心 EVPN Overlay 实现 |
| MPLS L3VPN | RFC 4364 | BGP/MPLS VPN 架构 |
| BGP 标签传播 | RFC 3107 / 8277 | BGP-LU 标签分发机制 |

---

## 九、总结

VXLAN 提供 **数据面隧道封装（VNI 粒度）**；  
EVPN 提供 **控制面路由分发（Route Type 1–5）**。

- Type 2：MAC/IP 学习 + ARP 抑制  
- Type 3：广播域注册 + BUM 控制  
- Type 5：三层互通（跨 L2VNI）  
- Type 1+4：多宿主 DF 控制

**L2VNI 必须一致才能二层互通；**  
**L3VNI 可不同，只要 RT 一致即可三层互通。**
