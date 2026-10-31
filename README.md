# Parakh

Forward a suspicious notice, stock tip, adviser or loan app. Parakh checks it against live official Indian records (SEBI, RBI, CBIC, Income Tax, eCourts, PIB Fact Check) and tells you what it found, where, when, and what to do next.

Built at the Forge AI buildathon (NxtWave) by Vihan, Rahul and Atharva. Problem statement T1.4.

## Run it

```
pip install -r requirements.txt
cp .env.example .env      # then add your ANTHROPIC_API_KEY
streamlit run app.py
```

## Docs

- [CLAUDE.md](CLAUDE.md): what we're building, rules, architecture, connector contract
- [docs/market-analysis.md](docs/market-analysis.md): problem size, competitors, data access, positioning
