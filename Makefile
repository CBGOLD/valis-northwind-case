# Northwind trust slice — everything is Python 3.9+ stdlib; no installs.
PY ?= python3

.PHONY: demo build test check fresh clean all

all: check build test

demo:            ## answer the CEO's questions in the terminal, with receipts
	$(PY) ask.py q1
	@echo
	$(PY) ask.py q2
	@echo
	$(PY) ask.py workflow
	@echo
	$(PY) ask.py value

build:           ## regenerate everything under out/ and fixtures/ (deterministic)
	$(PY) ask.py build
	$(PY) recon.py demo

test:            ## run the full test suite
	$(PY) -m unittest discover -s tests -t . -v

check:           ## re-verify every citation against the raw bundle
	$(PY) ask.py check

fresh:           ## prove the recon engine is not fitted to the committed fixture
	$(PY) recon.py fixture --seed 99 --outdir /tmp/northwind-fresh
	$(PY) recon.py run --crm /tmp/northwind-fresh/SYNTHETIC_crm_deals_2026-06.csv \
	  --invoices /tmp/northwind-fresh/SYNTHETIC_invoices_2026-06.csv \
	  --payouts /tmp/northwind-fresh/SYNTHETIC_payouts_2026-06.csv \
	  --outdir /tmp/northwind-fresh/out

clean:           ## remove generated artifacts (build recreates them byte-identically); keeps authored files like fixtures/README.md
	rm -rf out
	rm -f fixtures/SYNTHETIC_*.csv fixtures/fixture_manifest.json
