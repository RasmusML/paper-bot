FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt requirements.txt
COPY pyproject.toml pyproject.toml

COPY src/ src/
COPY queries/ queries/
COPY scripts/slack/aws_lambda/run_bot.py scripts/slack/aws_lambda/run_bot.py
COPY .env .env

RUN pip install -e .

CMD [ "scripts/slack/aws_lambda/run_bot.handler" ]