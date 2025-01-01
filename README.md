# Discord Servers

A repository is necessary to properly configure your routing in case they are not available on premises at a location.
- The script **automatically** retrieves IP addresses of all available Discord voice chat servers for every region.

## Regions
List of known and available regions:
> atlanta, brazil, bucharest, buenos-aires, dubai, finland, frankfurt, hongkong, india, japan, madrid, milan, newark, rotterdam, russia, santa-clara, santiago, seattle, singapore, south-korea, southafrica, stage-scale, stockholm, sydney, tel-aviv, us-central, us-east, us-south, us-west, warsaw, st-pete, dammam, jakarta, montreal, oregon

## Usage
### With [ipset](https://ipset.netfilter.org/ipset.man.html) or [kvas](https://github.com/qzeleza/kvas)
Install "bash" and "wget" package if you haven't
```sh
# For kvas and entware/openwrt systems
opkg update
opkg install bash
opkg install wget
```
Run the script
```sh
wget -O - https://raw.githubusercontent.com/Maks-gaming/discord-servers/refs/heads/main/kvas-adder.sh | bash
```
Then just select your target IPSet list and select crontab autoupdate time. Done!

## Local start
To run the script yourself, bend the repository and run the script by specifying the region:
```sh
python ./src/generate_voice_ip_list.py {region}
```