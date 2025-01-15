#!/opt/bin/bash

# Color definitions
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
MAGENTA="\033[35m"
CYAN="\033[36m"
BOLD="\033[1m"
NC="\033[0m" # No color

# Function to get absolute path
get_absolute_path() {
    local path="$1"
    echo "$(cd "$(dirname "$path")" && pwd)/$(basename "$path")"
}

# URLs for downloading IP lists
VOICE_IP_LIST_URL="https://raw.githubusercontent.com/Maks-gaming/discord-servers/refs/heads/main/data/voice-ip-list.txt"
BASE_IP_LIST_URL="https://raw.githubusercontent.com/Maks-gaming/discord-servers/refs/heads/main/data/base-ip-list.txt"

# Command-line flags
IPSET_NAME=""

# Process arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --ipset) IPSET_NAME="$2"; shift ;;
        *) echo -e "${RED}Unknown parameter: $1${NC}"; exit 1 ;;
    esac
    shift
done

# Fetch available ipsets if no --ipset provided
if [ -z "$IPSET_NAME" ]; then
    echo -e "${CYAN}Fetching list of available ipsets...${NC}"
    ipsets=$(ipset list -n | grep -vE '(^_NDM|^_UPNP)')
    ipsets_array=($ipsets)

    if [ ${#ipsets_array[@]} -eq 0 ]; then
        echo -e "${RED}No ipsets found. Exiting.${NC}"
        exit 1
    fi

    echo -e "${YELLOW}Please select a list by number:${NC}"
    i=1
    for ipset in "${ipsets_array[@]}"; do
        if [[ "$ipset" == "KVAS_LIST" || "$ipset" == "unblock" ]]; then
            echo -e "${BOLD}$i) $ipset ${GREEN}(recommended)${NC}"
        else
            echo -e "${BOLD}$i) $ipset${NC}"
        fi
        ((i++))
    done

    read -p "Enter the number corresponding to the desired ipset: " SELECTED_INDEX
    if [[ ! $SELECTED_INDEX =~ ^[0-9]+$ ]] || [ $SELECTED_INDEX -lt 1 ] || [ $SELECTED_INDEX -gt ${#ipsets_array[@]} ]; then
        echo -e "${RED}Invalid selection. Exiting.${NC}"
        exit 1
    fi

    IPSET_NAME=${ipsets_array[$((SELECTED_INDEX - 1))]}

    # Setup cron job
    echo -e "${CYAN}Choose the cron job option:${NC}"
    echo -e "${BOLD}1)${NC} Execute on every reboot"
    echo -e "${BOLD}2)${NC} Execute every day at 00:00"
    echo -e "${BOLD}3)${NC} Execute every day at 00:00 and on reboot"
    echo -e "${BOLD}4)${NC} Do not execute"
    read -p "Enter your choice (1-4): " CRON_OPTION

    CRONTAB_OUTPUT=$(crontab -l 2>/dev/null || true)
    SCRIPT_PATH=$(get_absolute_path "$0")
    SCRIPT_TO_RUN="$SCRIPT_PATH --ipset $IPSET_NAME"

    # Remove previous entries
    CRONTAB_OUTPUT=$(echo "$CRONTAB_OUTPUT" | grep -v "$SCRIPT_TO_RUN")

    case $CRON_OPTION in
        1)
            echo -e "${GREEN}Setting up cron job to execute on every reboot...${NC}"
            REBOOT_CRON_ENTRY="@reboot cd $(dirname "$SCRIPT_PATH") && /opt/bin/bash $SCRIPT_TO_RUN"
            CRONTAB_OUTPUT="$CRONTAB_OUTPUT"$'\n'"$REBOOT_CRON_ENTRY"
            ;;
        2)
            echo -e "${GREEN}Setting up cron job to execute every day at 00:00...${NC}"
            MIDNIGHT_CRON_ENTRY="0 0 * * * cd $(dirname "$SCRIPT_PATH") && /opt/bin/bash $SCRIPT_TO_RUN"
            CRONTAB_OUTPUT="$CRONTAB_OUTPUT"$'\n'"$MIDNIGHT_CRON_ENTRY"
            ;;
        3)
            echo -e "${GREEN}Setting up cron jobs for every day at 00:00 and on reboot...${NC}"
            REBOOT_CRON_ENTRY="@reboot cd $(dirname "$SCRIPT_PATH") && /opt/bin/bash $SCRIPT_TO_RUN"
            MIDNIGHT_CRON_ENTRY="0 0 * * * cd $(dirname "$SCRIPT_PATH") && /opt/bin/bash $SCRIPT_TO_RUN"
            CRONTAB_OUTPUT="$CRONTAB_OUTPUT"$'\n'"$REBOOT_CRON_ENTRY"$'\n'"$MIDNIGHT_CRON_ENTRY"
            ;;
        4)
            echo -e "${YELLOW}No cron job will be set.${NC}"
            ;;
        *)
            echo -e "${RED}Invalid cron option. Exiting.${NC}"
            exit 1
            ;;
    esac

    # Apply the new crontab
    echo "$CRONTAB_OUTPUT" | crontab -
    echo -e "${GREEN}Cron job setup complete.${NC}"
else
    echo -e "${CYAN}Skipping cron setup as --ipset is provided.${NC}"
fi

# Download IP addresses
echo -e "${CYAN}Downloading IP addresses from $VOICE_IP_LIST_URL and $BASE_IP_LIST_URL...${NC}"
voice_ip_list=$(curl -s "$VOICE_IP_LIST_URL")
base_ip_list=$(curl -s "$BASE_IP_LIST_URL")

if [ -z "$voice_ip_list" ] || [ -z "$base_ip_list" ]; then
    echo -e "${RED}Failed to fetch IP addresses. Exiting.${NC}"
    exit 1
fi

# Combine and process IP lists
combined_ip_list=$(echo -e "$voice_ip_list\n$base_ip_list" | sort -u)

# Optimized IP address addition
existing_ips=$(ipset list "$IPSET_NAME" | sed -n '/^Members:/,$p' | tail -n +2 | awk '{ print $1 }' | sort)

declare -A existing_ips_array
while IFS= read -r ip; do
    ip="${ip// }"
    if [[ -n "$ip" ]]; then
        existing_ips_array["$ip"]=1
    fi
done <<< "$existing_ips"

tmp_ipset_restore_file=$(mktemp)
while IFS= read -r ip; do
    ip="${ip// }"
    if [[ -z "${existing_ips_array["$ip"]-}" ]]; then
        echo "add $IPSET_NAME $ip -exist" >> "$tmp_ipset_restore_file"
        existing_ips_array["$ip"]=1
    fi
done <<< "$combined_ip_list"

if [[ -s "$tmp_ipset_restore_file" ]]; then
    ipset restore < "$tmp_ipset_restore_file"
    count=$(wc -l < "$tmp_ipset_restore_file")
    echo -e "${GREEN}Loaded ${YELLOW}$count${GREEN} IP addresses into IPset list ${YELLOW}$IPSET_NAME${NC}"
else
    echo -e "${RED}No new IP addresses to add to IPset.${NC}"
fi

rm -f "$tmp_ipset_restore_file"
