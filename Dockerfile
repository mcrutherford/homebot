FROM gorialis/discord.py:3.9.4-buster-pypi-minimal

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY . .

#WORKDIR /app/homebot

CMD ["python", "-u", "./homebot/homebot.py"]