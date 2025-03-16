#!/bin/bash
# FIXME Somethings broke
# Make sure script is run as root
if [ $EUID -ne 0 ]; then
    echo "This script must be run as root."
    exit 1
fi

# Update kali
echo
echo "****Updating Kali****"
echo
sleep 2s
sudo apt update
sudo apt full-upgrade -y

# Install Default Tools
echo
echo "****Installing Default Tools****"
echo
sleep 2s
sudo apt install -y kali-linux-default

# Install More Tools
echo
echo "****Installing More Tools****"
echo
sleep 2s
list_tools=("kali-tools-hardware" "kali-tools-crypto-stego" "kali-tools-fuzzing" "kali-tools-802-11" "kali-tools-bluetooth" "kali-tools-voip" "kali-linux-labs")
for i in "${list_tools[@]}"; do
    sudo apt install -y $i
done

# Install Menu Items
echo
echo "****Installing Menu Items****"
echo
sleep 2s
list_menu=("kali-tools-information-gathering" "kali-tools-vulnerability" "kali-tools-web" "kali-tools-database" "kali-tools-passwords" "kali-tools-wireless" "kali-tools-reverse-engineering" "kali-tools-exploitation" "kali-tools-social-engineering" "kali-tools-sniffing-spoofing" "kali-tools-post-exploitation" "kali-tools-forensics" "kali-tools-reporting")
for i in "${list_menu[@]}"; do
    sudo apt install -y $i
done

# Update again
echo
echo "****Checking for Updates****"
echo
sleep 2s
sudo apt update
sudo apt full-upgrade -y

# Install Git
echo
echo "****Installing Git****"
echo
sleep 2s
sudo apt install -y git

# Configure Git
echo
read -p "Would you like to configure Git? (y/n): " configure
if [ $configure == "y" ]; then
    echo
    echo "****Configuring Git****"
    echo
    sleep 2s
    echo
    read -p "Enter your name for Git: " name
    read -p "Enter your email for Git: " email
    read -p "Enter your Personal Access Token for Git: " token
    git config --global credential.helper store
    git config --global user.name $name
    git config --global user.email $email
    git config --global user.token $token
else
    echo
    echo "****Skipping Git Configuration****"
    echo
fi

# Install Misc Tools
echo
echo "****Installing Misc Tools and Packages****"
echo
sleep 2s
sudo apt install -y gobuster
sudo apt install -y tor
if [ -n "$(git config --global user.name)" ] && [ -n "$(git config --global user.email)" ]; then
    mkdir ~/packages
    git clone https://github.com/danielmiessler/SecLists.git ~/packages/SecLists
    git clone https://github.com/lgandx/Responder.git ~/packages/Responder
else
    echo "Git is not configured. Skipping cloning repositories."
fi

# Fix Installs
echo
echo "****Fixing Installs****"
echo
sleep 2s
sudo apt --fix-broken install -y

# Cleanup
echo
echo "****Cleaning Up****"
echo
sleep 2s
sudo apt autoremove -y
sudo apt autoclean -y

# Ask to Reboot
echo
read -p "Would you like to reboot now? (y/n): " reboot
if [ $reboot == "y" ]; then
    sudo reboot
else
    echo
    echo "****Setup Complete****"
    echo
fi
