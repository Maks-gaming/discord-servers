# Discord Servers

A repository is necessary to properly configure your routing in case they are not available on premises at a location.
- The script **automatically** retrieves IP addresses of all available Discord voice chat servers for every region.

## Usage
File with all IP addresses of Discord voice servers: https://github.com/Maks-gaming/discord-servers/blob/main/ip_list.txt

## Regions
List of known and available regions:
> atlanta, brazil, bucharest, buenos-aires, dubai, finland, frankfurt, hongkong, india, japan, madrid, milan, newark, rotterdam, russia, santa-clara, santiago, seattle, singapore, south-korea, southafrica, stage-scale, stockholm, sydney, tel-aviv, us-central, us-east, us-south, us-west, warsaw, st-pete, dammam, jakarta, montreal, oregon

## Local start
To run the script yourself, bend the repository and run the script by specifying the region:
```
python ./src/generate_voice_ip_list.py {region}
```