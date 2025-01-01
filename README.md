# Discord Servers 🌐
This repository helps you configure your routing system by automatically retrieving the IP addresses of all available Discord voice chat servers for different regions. This is particularly useful when servers are unavailable or need proper routing adjustments.

## 🌍 Available Regions
> atlanta, brazil, bucharest, buenos-aires, dubai, finland, frankfurt, hongkong, india, japan, madrid, milan, newark, rotterdam, russia, santa-clara, santiago, seattle, singapore, south-korea, southafrica, stage-scale, stockholm, sydney, tel-aviv, us-central, us-east, us-south, us-west, warsaw, st-pete, dammam, jakarta, montreal, oregon

## 🛠️ Usage
### 🔧 Using with `kvas` or `ipset`
> If you’re using kvas or entware/openwrt systems, follow these steps to set up the script:
#### Install prerequisites:
Make sure you have bash and curl installed:

```sh
opkg update
opkg install bash
opkg install curl
```

#### Run the script:
Use the following command to automatically fetch and configure the IP addresses:
```sh
curl -O https://raw.githubusercontent.com/Maks-gaming/discord-servers/main/kvas-adder.sh && bash kvas-adder.sh
```

#### Configuration:
- Choose your desired IPSet list.
- Set your crontab autoupdate frequency.

That’s it! 🎉

## ⚙️ Running Locally
If you want to run the script locally, simply clone the repository and specify your target region:

1. Clone the repository:
```sh
git clone https://github.com/Maks-gaming/discord-servers.git
cd discord-servers
```

2. Run the script:
```sh
python ./src/generate_voice_ip_list.py [region]
```
Replace `[region]` with the region of your choice (e.g., us-east, brazil, singapore).
