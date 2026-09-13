# Local adapter until upstream nlp-service/requirements.txt declares env2llm.
# Build the upstream nlp-service image first; this never starts a workflow.
FROM nlp2dsl-nlp-service:latest
COPY packages/dsl-contracts /opt/packages/dsl-contracts
COPY packages/dsl-validate /opt/packages/dsl-validate
RUN pip install --no-cache-dir env2llm==0.1.14 /opt/packages/dsl-contracts /opt/packages/dsl-validate \
    && python -c "from app.main import app; assert app is not None"
