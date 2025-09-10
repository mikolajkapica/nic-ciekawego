FROM ocaml/opam:ubuntu-22.04-ocaml-5.1

ENV DEBIAN_FRONTEND=noninteractive \
    OPAMYES=1

USER root
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git curl ca-certificates pkg-config build-essential m4 libgmp-dev libssl-dev zlib1g-dev \
    && rm -rf /var/lib/apt/lists/*

# Prepare workspace directory (bind-mounted by devcontainer)
WORKDIR /workspaces/nic-ciekawego

# Ensure opam user owns workspace
RUN chown -R opam:opam /workspaces
USER opam

# Initialize opam (already initialized in base image, but ensure up to date)
RUN opam update

# Pre-create local switch for faster startup (optional)
RUN opam switch show

CMD ["bash"]
