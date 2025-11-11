# 📘 EVPN / VXLAN 控制平面白皮书  
**作者：Helen Liu**  
*(Computer Science & Network Systems)*

---

## 一、🧱 ESI / EVI / VNI 核心概念与区别

### 🔹 定义对比表

| 名称 | 全称 | 所属层级 | 平面类型 | 作用 |
|------|------|-----------|-----------|------|
| **ESI** | Ethernet Segment Identifier | 接入层 (CE–PE) | 控制平面 | 标识同一 CE 接入多个 PE 的以太段，用于 DF 选举、防环 |
| **EVI** | EVPN Instance | 控制层 | 控制平面 | 标识 EVPN 广播域（租户实例），对应 EVPN 控制平面的一次实例 |
| **VNI** | VXLAN Network Identifier | Overlay 层 | 数据平面 | 24 位 VXLAN 封装 ID，用于区分不同 Overlay 网络（逻辑广播域） |

---

### 🔹 三者层级关系图

```
物理接入层：CE ↔ PE (ESI)
控制平面层：EVI ↔ EVPN Instance
数据封装层：VNI ↔ VXLAN Network Identifier
```

🧭 **关系说明：**
- **ESI** → “谁接进来”（CE–PE 接入段）
- **EVI** → “控制哪个逻辑广播域”（EVPN 实例）
- **VNI** → “封装属于哪个 Overlay 网络”（VXLAN 隧道）

---

### 🔹 控制面与数据面的映射关系

| 层级 | 控制面字段 | 数据面字段 | 功能 |
|------|-------------|-------------|------|
| 二层广播域 | EVI | L2VNI | MAC/IP 学习与泛洪控制 |
| 三层路由域 | VRF (EVI) | L3VNI | 跨子网前缀传播 |
| 接入段 | ESI | 无对应字段 | Dual-Homing DF 选举、防环 |

📘 一句话总结：  
> EVI ↔ VNI 是一一映射；  
> ESI 是独立的接入标识，用于 DF 选举（Type 4 路由）。

---

## 二、🧩 控制平面 BGP UPDATE 抓包结构（YAML 形式）

### 1️⃣ Type 2 – 单宿主 (Single-Homing)

```yaml
BGP UPDATE:
  Path-Attributes:
    - MP_REACH_NLRI:
        AFI: L2VPN
        SAFI: EVPN
        Next-Hop: 10.1.1.1
        NLRI:
          Route-Type: 2                   # MAC/IP Advertisement
          Fields:
            RD: 10.1.1.1:5001
            ESI: 00:00:00:00:00:00        # 单宿主
            Ethernet-Tag-ID: 5001         # L2VNI
            MAC-Address: 00:11:22:33:44:55
            IP-Address: 10.1.1.10         # 用于 ARP 抑制
            Label/VNI: 5001
  Extended-Communities:
    - RT: 100:5001
    - MAC-Mobility: Seq# 0
  NLRI-Type: Type 2 (MAC/IP Advertisement)
  Purpose: >
    通告单宿主主机的 MAC/IP → VTEP 映射；
    支持远端 ARP 抑制，无需数据面泛洪。
```

---

### 2️⃣ Type 2 – 双宿主 (Multi-Homing)

```yaml
BGP UPDATE:
  Path-Attributes:
    - MP_REACH_NLRI:
        AFI: L2VPN
        SAFI: EVPN
        Next-Hop: 10.1.1.1
        NLRI:
          Route-Type: 2
          Fields:
            RD: 10.1.1.1:5001
            ESI: 00:00:00:00:00:01        # 非零 => 多宿主段
            Ethernet-Tag-ID: 5001
            MAC-Address: aa:bb:cc:dd:ee:ff
            IP-Address: 10.1.1.20
            Label/VNI: 5001
  Extended-Communities:
    - RT: 100:5001
    - ESI-Label: 100                      # DF 防环标识
    - MAC-Mobility: Seq# 1
  NLRI-Type: Type 2 (MAC/IP Advertisement)
  Purpose: >
    通告双宿主主机的 MAC/IP 映射；
    多个 PE 共享 ESI，控制平面协调 DF；
    数据面通过 ESI-Label 防环。
```

---

### 3️⃣ Type 4 – Ethernet Segment Route (DF 选举)

```yaml
BGP UPDATE:
  Path-Attributes:
    - MP_REACH_NLRI:
        AFI: L2VPN
        SAFI: EVPN
        Next-Hop: 10.1.1.1
        NLRI:
          Route-Type: 4
          Fields:
            ESI: 00:00:00:00:00:01
            Originating-Router-IP: 10.1.1.1
  Extended-Communities:
    - DF-Algorithm: HRW                  # DF 算法类型
    - DF-Preference: 32768               # 优先级 (可选)
    - ES-Import RT: 65000:1
  Purpose: >
    向其他 PE 通告参与 ESI=0001 的成员；
    控制平面执行 DF 选举与环路防护。
```

---

### 4️⃣ Type 5 – IP Prefix Route (L3VNI)

```yaml
BGP UPDATE:
  Path-Attributes:
    - MP_REACH_NLRI:
        AFI: L2VPN
        SAFI: EVPN
        Next-Hop: 10.1.1.1
        NLRI:
          Route-Type: 5
          Fields:
            RD: 10.1.1.1:6001
            ESI: 00:00:00:00:00:00
            Ethernet-Tag-ID: 0
            IP-Prefix: 10.1.2.0/24
            GW-IP: 10.1.1.1
            Label/VNI: 6001
  Extended-Communities:
    - RT: 100:6001
    - VRF: Tenant-A
  NLRI-Type: Type 5 (IP Prefix Route)
  Purpose: >
    通告 L3VNI 前缀，用于跨子网互通；
    典型场景：L2VNI ↔ L3VNI ↔ L2VNI。
```

---

## 三、⚙️ DF 选举算法机制

### 🔹 HRW 算法（Highest Random Weight）

- 不需要为每个 VLAN 手动设置；
- 所有 PE 使用相同算法：
  ```
  Hash(VLAN-ID, Router-IP)
  结果最高的为 DF
  ```
- 不同 VLAN 可分配不同 DF → 实现负载均衡；
- 结果分布一致，无需协调。
