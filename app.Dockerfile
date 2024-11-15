FROM python:3.11-bookworm

WORKDIR /

COPY dependencies.txt .
RUN pip install --no-cache-dir -r dependencies.txt

COPY . .

CMD ["python3", "madhacks2024.py"]