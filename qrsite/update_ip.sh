#!/bin/bash

IP=$(curl -s https://api.ipify.org)
    ENV_FILE="/home/s4vant/qrproject/qrMaker/qrsite/.env"

# удалим старую строку IP_ADDRESS и добавим новую
sed -i '/^IP_ADDRESS=/d' "$ENV_FILE"
echo "IP_ADDRESS=$IP" >> "$ENV_FILE"
