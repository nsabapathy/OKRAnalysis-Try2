# LLM Provider Configuration Guide

This system supports multiple LLM providers for OKR analysis. You can easily switch between providers by updating the `.env` file.

## Supported Providers

### 1. Google Gemini (Default)

**Models Available:**
- `gemini-2.5-flash-lite` (Recommended - Fast and cost-effective)
- `gemini-2.0-flash-exp` (Experimental features)
- `gemini-pro` (Higher quality, more expensive)

**Configuration:**
```bash
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash-lite
```

**Getting API Key:**
1. Visit https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Create new API key
4. Copy to `.env` file

**Pricing:**
- Input: $0.075 per 1M tokens
- Output: $0.30 per 1M tokens

### 2. Qwen (Alibaba Cloud)

**Models Available:**
- `qwen-plus` (Recommended - Balanced performance)
- `qwen-turbo` (Faster, lower cost)
- `qwen-max` (Highest quality)

**Configuration:**
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=your_qwen_api_key_here
QWEN_MODEL=qwen-plus
```

**Getting API Key:**
1. Visit https://dashscope.aliyun.com/
2. Sign up for Alibaba Cloud account
3. Navigate to DashScope console
4. Create API key
5. Copy to `.env` file

**Pricing:**
- Qwen-Plus: ¥0.004 per 1K tokens (~$0.0006 USD)
- Qwen-Turbo: ¥0.002 per 1K tokens (~$0.0003 USD)
- Qwen-Max: ¥0.04 per 1K tokens (~$0.006 USD)

## Switching Providers

To switch between providers:

1. Open `.env` file
2. Change `LLM_PROVIDER` to either `gemini` or `qwen`
3. Ensure the corresponding API key is set
4. Optionally update the model name
5. Save the file
6. Run your analysis - no code changes needed!

## Testing Your Configuration

### Test Gemini Connection
```bash
python test_gemini.py
```

### Test Qwen Connection
```bash
python test_qwen.py
```

Both tests should return "OK" if configured correctly.

## Provider Comparison

| Feature | Gemini | Qwen |
|---------|--------|------|
| Speed | Fast | Very Fast |
| Cost (500 OKRs) | ~$0.30 | ~$0.05-0.10 |
| JSON Support | Native | Via OpenAI API |
| Language Support | Excellent | Excellent (especially Chinese) |
| Rate Limits | Generous | Generous |
| Availability | Global | Global (via Alibaba Cloud) |

## Recommendations

- **For English OKRs**: Either provider works well
- **For Chinese/Multilingual OKRs**: Qwen may perform better
- **For cost optimization**: Qwen is significantly cheaper
- **For simplicity**: Gemini has simpler setup
- **For speed**: Both are fast, Qwen slightly faster

## Implementation Details

The system uses a unified `LLMClient` abstraction that handles:
- Provider-specific API calls
- Response formatting
- Error handling
- Token counting
- JSON response parsing

All analysis modules (`OKRAnalyzer`, `ThemeExtractor`, `QualityScorer`, etc.) work seamlessly with both providers without any code changes.

## Troubleshooting

### "Invalid LLM_PROVIDER" error
- Check that `LLM_PROVIDER` is set to either `gemini` or `qwen` (lowercase)

### "API key not found" error
- Verify the API key for your selected provider is set in `.env`
- Make sure there are no extra spaces or quotes around the key

### "openai package required for Qwen" error
- Run: `pip install -r requirements.txt`
- This will install the OpenAI package needed for Qwen compatibility

### Different response quality between providers
- Try adjusting `TEMPERATURE` (0.0-1.0) in `.env`
- Test different model variants (e.g., qwen-max vs qwen-plus)
- Both providers should give comparable results for OKR analysis
