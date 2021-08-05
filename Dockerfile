FROM gorialis/discord.py:3.9.4-buster-pypi-minimal

WORKDIR /app

COPY requirements.txt ./
RUN pip install -r requirements.txt

#COPY . /homebot
COPY . .

CMD ["python", "-u", "homebot.py"]