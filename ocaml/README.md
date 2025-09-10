# OCaml Rewrite of Daily News Summarizer

This directory contains an in‑progress rewrite of the Python news summarizer in OCaml using Lwt for async workflows.

## High-Level Architecture

Modules (planned / scaffolded):

- `Article` – immutable record representing a fetched article
- `Config` – load and validate YAML configuration & env vars
- `Rss_fetch` – fetch & parse RSS feeds concurrently with retries
- `Translate` – translate non‑Polish text to Polish via OpenRouter (LLM) API
- `Summarize` – create grouped story summaries from article corpus via LLM
- `Format_email` – produce HTML email body
- `Send_email` – build MIME and send through Gmail SMTP (to be implemented with `mrmime` + `colombe` + `tls`)
- `Main` – orchestration pipeline

## Dependencies (opam)

```
cohttp-lwt-unix
yojson
lwt
ptime
yaml
logs
fmt
mrmime
colombe
emile
tls
ca-certs
sexp_conv
ppx_deriving_yojson
```

Some dependencies (e.g. SMTP stack) may evolve if a simpler SMTP client becomes available.

## Build

```
opam switch create . 5.1.1 --deps-only --yes
opam install . --deps-only -y
dune build
```

## Running

```
dune exec news_summarizer
```

Environment variables expected (planned):

- `OPENROUTER_API_KEY`
- `GMAIL_USERNAME`
- `GMAIL_APP_PASSWORD`

## Status

Scaffold only. Network calls and SMTP sending are placeholders.

## Next Steps

1. Flesh out RSS parsing (XML / feed handling)
2. Implement real translation & summarization HTTP calls
3. Implement MIME + SMTP send
4. Add tests (alcotest) for pure modules
5. Add retry/backoff strategy (Lwt + exponential) in fetch
