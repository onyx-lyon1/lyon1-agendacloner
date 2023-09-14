# 📅 lyon1-agendaCloner

A Python project for cloning Lyon 1 ADE (Agenda) and generating the ICS URL for each category.

⚠️ **Disclaimer:** This project is experimental and not stable. The developer is not responsible for any damage it may cause. Please ensure you handle RGPD and privacy concerns appropriately.

## ✨ Features

- Clone the Lyon 1 ADE agenda tree to retrieve category IDs.
- Generate ICS URLs for each category.

## ⚙️ Installation

1. Install the required dependencies by running the following command:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file in the project directory and add your Lyon 1 ADE credentials:

```bash
echo "USERNAME=YOUR_USERNAME" > .env
echo "PASSWORD=YOUR_PASSWORD" >> .env
```

## 🔒 Usage

To clone the Lyon 1 ADE agenda and generate the ICS URLs for each category, run the following command:

```bash
python agenda_clonner.py
```
