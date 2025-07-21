FROM python:3-alpine
WORKDIR /app
RUN --mount=type=bind,source=requirements.txt,dst=requirements.txt pip install -r requirements.txt
COPY main.py .
ENTRYPOINT [ "python3" ]
CMD [ "main.py" ]
