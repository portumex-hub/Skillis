# Which Free LLM API Should You Use?

Use this decision tree to pick the right API for your use case.

## Decision Tree

```
Do you need the fastest possible inference?
├── YES → Use Groq (Llama 3.3 70B, 14,400 req/day)
│         https://console.groq.com
│
└── NO → Do you need a huge context window (>100K tokens)?
         ├── YES → Use Google Gemini Flash (1M context, free)
         │         https://aistudio.google.com
         │
         └── NO → Do you need multimodal (images + text)?
                  ├── YES → Use Google Gemini Flash
                  │
                  └── NO → Do you need the best open-source model?
                           ├── YES → Use Together AI ($5 free credit, 50+ models)
                           │         https://together.ai
                           │
                           └── NO → Are you in Europe (GDPR)?
                                    ├── YES → Use Mistral AI
                                    │         https://mistral.ai
                                    │
                                    └── NO → Use OpenRouter (aggregates all)
                                             https://openrouter.ai
```

## Side-by-Side Comparison

| Criteria | Groq | Gemini Flash | Mistral | Together AI | OpenRouter |
|----------|------|-------------|---------|-------------|------------|
| Speed | ⚡⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡ | ⚡⚡ |
| Free Limit | 14,400/day | 1,500/day | 500M tok/mo | $5 credit | Varies |
| Context | 128K | 1M | 32K | Varies | Varies |
| Multimodal | ❌ | ✅ | ❌ | Some | Some |
| No CC | ✅ | ✅ | ✅ | ✅ | ✅ |
| Best For | Speed | Long docs | Privacy | Variety | Flexibility |

## My Recommendation

**Default choice for most projects:** Groq with Llama 3.3 70B

It's the fastest, has generous limits, needs no credit card, and the model quality
is competitive with GPT-4o for most tasks. Use Gemini Flash when you need vision
or very long context windows.
