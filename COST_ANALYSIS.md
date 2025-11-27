# Token Usage & Cost Analysis

## Token Usage Per Resume Parse

### Input Tokens

1. **System Prompt**: ~350-400 tokens
   - The extraction prompt with JSON schema is approximately 1,200-1,500 characters
   - Converted to tokens: ~350-400 tokens

2. **User Message**: ~1,200-2,500 tokens (varies by resume length)
   - Prefix: "Parse this resume:\n\n" = ~10 tokens
   - Resume text: 
     - **1-page resume**: ~500-800 words = ~600-1,000 tokens
     - **2-page resume**: ~1,000-1,600 words = ~1,200-2,000 tokens
     - **3-page resume**: ~1,500-2,400 words = ~1,800-3,000 tokens
   - **Average**: ~1,500 tokens

**Total Input**: ~1,900 tokens (system + average resume)

### Output Tokens

**JSON Response**: ~1,500-3,000 tokens
- Simple resume (basic info): ~1,000-1,500 tokens
- Detailed resume (multiple experiences, projects, etc.): ~2,000-3,000 tokens
- **Average**: ~2,000 tokens

### Total Tokens Per Parse

- **Input**: ~1,900 tokens
- **Output**: ~2,000 tokens
- **Total**: ~3,900 tokens per resume

---

## Cost Per Resume (OpenAI Pricing as of 2024)

### GPT-4o Pricing
- **Input**: $2.50 per 1M tokens
- **Output**: $10.00 per 1M tokens

**Cost per resume (GPT-4o)**:
- Input cost: 1,900 tokens × ($2.50 / 1,000,000) = **$0.00475**
- Output cost: 2,000 tokens × ($10.00 / 1,000,000) = **$0.02000**
- **Total: ~$0.025 per resume** (2.5 cents)

### GPT-5.1 Pricing
- **Input**: ~$5.00 per 1M tokens (estimated, may vary)
- **Output**: ~$15.00 per 1M tokens (estimated, may vary)

**Cost per resume (GPT-5.1)**:
- Input cost: 1,900 tokens × ($5.00 / 1,000,000) = **$0.0095**
- Output cost: 2,000 tokens × ($15.00 / 1,000,000) = **$0.03000**
- **Total: ~$0.04 per resume** (4 cents)

---

## Monthly Cost Estimates

### Scenario 1: Light Usage (100 resumes/month)
- **GPT-4o**: 100 × $0.025 = **$2.50/month**
- **GPT-5.1**: 100 × $0.04 = **$4.00/month**

### Scenario 2: Moderate Usage (1,000 resumes/month)
- **GPT-4o**: 1,000 × $0.025 = **$25.00/month**
- **GPT-5.1**: 1,000 × $0.04 = **$40.00/month**

### Scenario 3: Heavy Usage (10,000 resumes/month)
- **GPT-4o**: 10,000 × $0.025 = **$250.00/month**
- **GPT-5.1**: 10,000 × $0.04 = **$400.00/month**

### Scenario 4: Using Both Models (Comparison Mode)
If parsing with both GPT-4o and GPT-5.1:
- **Per resume**: $0.025 + $0.04 = **$0.065** (6.5 cents)
- **1,000 resumes**: **$65.00/month**

---

## Cost Optimization Tips

1. **Use GPT-4o for most cases**: 40% cheaper than GPT-5.1
2. **Cache results**: If same resume is parsed multiple times, cache the result
3. **Batch processing**: Process multiple resumes in one session to reduce overhead
4. **Truncate very long resumes**: Limit to first 3-4 pages if resume is extremely long
5. **Use GPT-4o by default**: Only use GPT-5.1 when higher accuracy is needed

---

## Token Usage Breakdown Example

**Example: 2-page resume**

```
System Prompt:        400 tokens
User Message Prefix:   10 tokens
Resume Text:        1,500 tokens
─────────────────────────────
Total Input:       1,910 tokens

JSON Response:      2,200 tokens
─────────────────────────────
Total Output:      2,200 tokens

GRAND TOTAL:       4,110 tokens
```

**Cost (GPT-4o)**: 
- Input: 1,910 × $2.50/1M = $0.00478
- Output: 2,200 × $10.00/1M = $0.02200
- **Total: $0.02678**

---

## Real-World Estimates

Based on typical resume parsing scenarios:

| Resume Type | Input Tokens | Output Tokens | Total Tokens | Cost (GPT-4o) |
|------------|--------------|---------------|--------------|---------------|
| Simple (1 page) | 1,400 | 1,200 | 2,600 | $0.016 |
| Average (2 pages) | 1,900 | 2,000 | 3,900 | $0.025 |
| Detailed (3 pages) | 2,500 | 2,800 | 5,300 | $0.033 |
| Complex (4+ pages) | 3,200 | 3,500 | 6,700 | $0.042 |

**Average cost per resume: ~$0.025 (2.5 cents)**

---

## Notes

- Token counts are estimates based on typical resumes
- Actual usage may vary based on:
  - Resume formatting and length
  - Amount of detail in experience/projects
  - Number of sections included
- OpenAI pricing may change - check current rates at [OpenAI Pricing](https://openai.com/pricing)
- GPT-5.1 pricing is estimated and may differ when officially released

