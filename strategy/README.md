# SynthData — Strategy

## Product Vision

SynthData is the go-to platform for generating privacy-compliant synthetic data. We enable AI teams, QA engineers, and data-driven organizations to create realistic datasets without exposing real user data — covering tabular, text, and audio/speech modalities.

## Strategic Pillars

1. **Multi-modal generation** — Tabular, text, and audio data from a single platform
2. **Privacy-first** — Every generated record is synthetic; zero real PII exposure
3. **AudioText synergy** — Unique audio/speech niche via our sister product's AI expertise
4. **Developer experience** — Simple API, pre-built templates, fast time-to-data

## Roadmap

### Phase 1: Foundation (Current)
- [x] FastAPI backend skeleton
- [x] Generator architecture (base + tabular + text + audio)
- [x] Azure OpenAI integration
- [x] Azure Speech Services integration
- [ ] End-to-end tabular generation pipeline
- [ ] Job queue with async processing
- [ ] Frontend schema builder MVP

### Phase 2: Production (Next)
- [ ] Azure Blob Storage dataset lifecycle
- [ ] Authentication and API key management
- [ ] Rate limiting and usage metering
- [ ] CSV and Parquet export formats
- [ ] Pre-built schema template library (20+ templates)

### Phase 3: Audio Niche
- [ ] Multi-speaker conversation generation
- [ ] Background noise mixing
- [ ] Acoustic simulation (reverb, phone quality)
- [ ] Hugging Face dataset publishing
- [ ] AudioText customer cross-sell program

### Phase 4: Scale
- [ ] Custom Neural Voice support
- [ ] Image data generation (DALL-E)
- [ ] Dataset marketplace
- [ ] Enterprise SSO and audit logging
- [ ] SOC 2 Type II certification

## Current Priorities
1. Ship end-to-end tabular generation (POST → generate → download)
2. Build frontend schema builder MVP
3. Validate synthetic audio opportunity with 5 beta customers

## Competitive Landscape

| Competitor | Strength | SynthData Advantage |
|-----------|----------|-------------------|
| Gretel.ai | Tabular privacy models | Multi-modal (audio), simpler API |
| Mostly AI | Enterprise synthetic data | Audio niche, developer-first |
| Synthesis AI | Computer vision focus | Text + audio, Azure-native |
| Faker / Mimesis | Code libraries | AI-powered realism, no code needed |

## Key Metrics

| Metric | Target (6 months) |
|--------|-------------------|
| API requests/day | 1,000 |
| Datasets generated | 500 |
| Beta customers | 20 |
| MRR | $10,000 |

## Links
- [Company Strategy](https://github.com/fratei/creative-ware-hq/blob/main/strategy/README.md)
- [Product Card](https://github.com/fratei/creative-ware-hq/blob/main/products/synthdata.md)
- [Synthetic Audio Opportunity](opportunities/synthetic-audio-data.md)
