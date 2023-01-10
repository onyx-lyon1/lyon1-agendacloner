# lyon1-agendaClonner

This project is completly experimental and not stable. I'm not responsible for any damage it may cause. And take care of rgpd and privacy.

It enables you to completly clone the lyon1 ade agenda tree to get the id of all categories.

With this id, you can generate the ics url of the agenda.

## Usage

```bash
pip install -r requirements.txt
echo "USERNAME=YOUR_USERNAME" > .env
echo "PASSWORD=YOUR_PASSWORD" >> .env
python agenda_clonner.py
```