# OC Debug release-candidate image. Python standard library only: no pip or apt.
# Run with --read-only, --network none, --cap-drop ALL and a non-root user (see README).
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONNOUSERSITE=1

WORKDIR /opt/oc-debug
COPY skills ./skills
COPY tests ./tests
COPY examples ./examples
# Root-owned and not writable by the runtime user.
RUN chmod -R u=rwX,go=rX /opt/oc-debug

USER 65532:65532

ENTRYPOINT ["python", "-B", "/opt/oc-debug/skills/oc-debug/tools/oc_debug.py"]
CMD ["--help"]
