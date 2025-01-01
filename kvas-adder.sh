#!/bin/bash

# Function to select the IP set
select_ipset() {
  echo "Fetching list of available ipsets..."
  ipsets=$(ipset list -n | grep -vE '(^_NDM|^_UPNP)')
  ipsets_array=($ipsets)

  echo "Please select a list by number:"
  i=1
  for ipset in "${ipsets_array[@]}"; do
    echo "$i) $ipset"
    ((i++))
  done

  read -p "Enter the number corresponding to the list: " ipset_index
  selected_ipset="${ipsets_array[$ipset_index-1]}"
  echo "You have selected: $selected_ipset"
}

# Function to select the cron job option
select_cron_option() {
  echo "Choose the cron job option:"
  echo "1) Execute on every reboot"
  echo "2) Execute every day at 00:00"
  echo "3) Execute every day at 00:00 and on reboot"
  echo "4) Do not execute"
  
  read -p "Enter the number of your choice: " cron_option
  
  case $cron_option in
    1)
      cron_command="@reboot /path/to/this/script"
      echo "Will run on reboot."
      ;;
    2)
      cron_command="0 0 * * * /path/to/this/script"
      echo "Will run every day at 00:00."
      ;;
    3)
      cron_command="0 0 * * * /path/to/this/script && @reboot /path/to/this/script"
      echo "Will run every day at 00:00 and on reboot."
      ;;
    4)
      cron_command=""
      echo "No cron job will be set."
      ;;
    *)
      echo "Invalid choice. No cron job set."
      cron_command=""
      ;;
  esac
}

# Function to add IPs to the selected IP set
add_ips_to_ipset() {
  urls=(
    "https://raw.githubusercontent.com/Maks-gaming/discord-servers/refs/heads/main/data/base-ip-list.txt"
    "https://raw.githubusercontent.com/Maks-gaming/discord-servers/refs/heads/main/data/voice-ip-list.txt"
  )

  for url in "${urls[@]}"; do
    echo "Fetching IP list from $url..."
    ip_list=$(curl -s $url)

    while IFS= read -r ip; do
      # Add IP to the ipset and echo the status in the background
      ipset add "$selected_ipset" "$ip" >/dev/null 2>&1 &
      echo "Adding $ip to $selected_ipset" &
    done <<< "$ip_list"
  done
  wait  # Wait for all background processes to complete
}

# Main script execution

select_ipset
select_cron_option

# Set cron job if necessary
if [[ -n "$cron_command" ]]; then
  (crontab -l ; echo "$cron_command") | crontab -
  echo "Cron job set."
else
  echo "No cron job set."
fi

add_ips_to_ipset
echo "IP addresses have been added successfully to the selected IP set!"
