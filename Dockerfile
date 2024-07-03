FROM python:3.10.14

ENV VIRTUAL_ENV=/opt/venv
RUN python -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
COPY ./requirements.txt .

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app




# Install the dependencies
RUN pip install -r requirements.txt
RUN playwright install
RUN playwright install-deps


# Expose port 8000 to the outside world
EXPOSE 8000

# Run the command to start the server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
