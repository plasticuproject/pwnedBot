FROM python:3.11-alpine

RUN apk --no-cache add curl
RUN adduser -D bot
USER bot
WORKDIR /home/bot
COPY --chown=bot:bot pwned_bot.py .
COPY --chown=bot:bot requirements.txt .
COPY --chown=bot:bot images/ images/
ENV VIRTUAL_ENV=/home/bot/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
CMD ["python", "pwned_bot.py"]
