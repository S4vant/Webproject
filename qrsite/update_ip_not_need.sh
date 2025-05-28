#!/bin/bash

IP=$(curl -s https://api.ipify.org)

if [ -z "$IP" ]; then
    echo "[ERROR] Не удалось получить внешний IP"
    exit 1
fi

# Удаляем старую строку IP_ADDRESS
sed -i '/^IP_ADDRESS=/d' /home/s4vant/qrproject/qrMaker/qrsite/.env

# Добавляем новую строку
echo "IP_ADDRESS=$IP" >> /home/s4vant/qrproject/qrMaker/qrsite/.env
